from django.conf import settings

from .project import project_dir
from utility.runtime import Runtime

import os
import json
import threading


class TerraformError(Exception):
    pass


class Terraform(object):

    thread_lock = threading.Semaphore(settings.TERRAFORM_MAX_PROCESSES)


    def __init__(self, command, type, id, ignore = False):
        self.lib_type = 'terraform'
        self.command = command
        self.type = type
        self.id = id
        self.ignore = ignore
        self.initialize = False


    def get_project_name(self, manifest_path, variables):
        provider = os.path.basename(manifest_path).replace('.tf', '')
        return "{}.{}.{}".format(self.type, provider, self.id)


    def check_init(self, project):
        if not project.exists('.terraform'):
            self.initialize = True

    def init(self, project, display = False):
        if self.initialize:
            terraform_command = (
                'terraform',
                'init',
                '-force-copy'
            )
            success = self.command.sh(
                terraform_command,
                cwd = project.base_path,
                display = display,
                line_prefix = '[terraform]: '
            )
            if not success and not self.ignore:
                raise TerraformError("Terraform init failed: {}".format(" ".join(terraform_command)))


    def plan(self, manifest_path, variables, state, display_init = False):
        with project_dir(self.lib_type, self.get_project_name(manifest_path, variables)) as project:
            self.clean_project(project)
            self.check_init(project)

            project.copy(manifest_path, 'manifest.tf')
            self.save_variable_index(project, variables)
            if state:
                self.save_state(project, state)

            with self.thread_lock:
                self.init(project, display_init)

                terraform_command = (
                    'terraform',
                    'plan',
                    "-var-file={}".format(self.save_variables(project, variables))
                )
                success = self.command.sh(
                    terraform_command,
                    cwd = project.base_path,
                    display = True,
                    line_prefix = '[terraform]: '
                )

            if not Runtime.debug():
                self.clean_project(project)

            if not success and not self.ignore:
                raise TerraformError("Terraform plan failed: {}".format(" ".join(terraform_command)))


    def apply(self, manifest_path, variables, state, display_init = False):
        with project_dir(self.lib_type, self.get_project_name(manifest_path, variables)) as project:
            self.clean_project(project)
            self.check_init(project)

            project.copy(manifest_path, 'manifest.tf')
            self.save_variable_index(project, variables)
            if state:
                self.save_state(project, state)

            with self.thread_lock:
                self.init(project, display_init)

                terraform_command = (
                    'terraform',
                    'apply',
                    '-auto-approve',
                    "-var-file={}".format(self.save_variables(project, variables))
                )
                success = self.command.sh(
                    terraform_command,
                    cwd = project.base_path,
                    display = True,
                    line_prefix = '[terraform]: '
                )
            if not success and not self.ignore:
                if not Runtime.debug():
                    self.clean_project(project)
                raise TerraformError("Terraform apply failed: {}".format(" ".join(terraform_command)))

            self.command.info('')

            state = self.load_state(project)

            if not Runtime.debug():
                self.clean_project(project)
            return state


    def destroy(self, manifest_path, variables, state, display_init = False):
        with project_dir(self.lib_type, self.get_project_name(manifest_path, variables)) as project:
            self.clean_project(project)
            self.check_init(project)

            project.copy(manifest_path, 'manifest.tf')
            self.save_variable_index(project, variables)
            if state:
                self.save_state(project, state)

            with self.thread_lock:
                self.init(project, display_init)

                terraform_command = [
                    'terraform',
                    'destroy',
                    '-auto-approve',
                    "-var-file={}".format(self.save_variables(project, variables))
                ]
                success = self.command.sh(
                    terraform_command,
                    cwd = project.base_path,
                    display = True,
                    line_prefix = '[terraform]: '
                )
            if not Runtime.debug():
                self.clean_project(project)

            if not success and not self.ignore:
                raise TerraformError("Terraform destroy failed: {}".format(" ".join(terraform_command)))
            project.delete()


    def save_variable_index(self, project, variables):
        index = []

        for name, value in variables.items():
            if isinstance(value, dict):
                data_type = self.parse_object(value, '  ')
            elif isinstance(value, (list, tuple)):
                data_type = 'list(any)'
            else:
                data_type = 'string'

            index.extend([
                'variable "{}" {{'.format(name),
                '  type = {}'.format(data_type),
                '}'
            ])
        return project.save("\n".join(index), 'variables.tf')

    def parse_object(self, variables, prefix):
        object = ['object({']
        inner_prefix = prefix + '  '

        for key, value in variables.items():
            if isinstance(value, dict):
                object.append("{}{} = {}".format(inner_prefix, key, self.parse_object(value, inner_prefix)))
            elif isinstance(value, (list, tuple)):
                object.append("{}{} = list(any)".format(inner_prefix, key))
            else:
                object.append("{}{} = string".format(inner_prefix, key))

        object.append("{}}})".format(prefix))
        return "\n".join(object)


    def save_variables(self, project, variables):
        return project.save(json.dumps(variables, indent = 2), 'variables.tfvars.json')


    def save_state(self, project, state):
        return project.save(json.dumps(state, indent = 2), 'terraform.tfstate')

    def load_state(self, project):
        return json.loads(project.load('terraform.tfstate'))


    def clean_project(self, project):
        project.remove('variables.tfvars.json')
        project.remove('terraform.tfstate')
        project.remove('terraform.tfstate.backup')
