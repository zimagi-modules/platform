from django.conf import settings

from .data import dump_json, load_json
from .filesystem import FileSystem

import threading


TERRAFORM_VARS_FILE = 'variables.tfvars.json'
TERRAFORM_STATE_FILE = 'terraform.tfstate'


class TerraformError(Exception):
    pass


class Terraform(object):

    thread_lock = threading.Semaphore(settings.TERRAFORM_MAX_PROCESSES)


    def __init__(self, command, name, path, environment = None):
        if environment is None:
            environment = {}

        self.command = command
        self.name = name
        self.disk = FileSystem(path)
        self.environment = environment


    def init(self):
        terraform_command = (
            'terraform',
            'init',
            '-force-copy'
        )
        success = self.command.sh(
            terraform_command,
            cwd = self.disk.base_path,
            env = self.environment,
            line_prefix = '[terraform]: '
        )
        if not success:
            raise TerraformError("Terraform init failed: {}".format(" ".join(terraform_command)))


    def plan(self, variables, state = None):
        self.clean_project()

        if state:
            self.save_state(state)

        with self.thread_lock:
            self.init()

            terraform_command = (
                'terraform',
                'plan',
                "-var-file={}".format(self.save_variables(variables))
            )
            success = self.command.sh(
                terraform_command,
                cwd = self.disk.base_path,
                env = self.environment,
                line_prefix = '[terraform]: '
            )
        if not self.command.debug:
            self.clean_project()

        if not success:
            raise TerraformError("Terraform plan failed: {}".format(" ".join(terraform_command)))


    def apply(self, variables, state = None):
        self.clean_project()

        if state:
            self.save_state(state)

        with self.thread_lock:
            self.init()

            terraform_command = (
                'terraform',
                'apply',
                '-auto-approve',
                "-var-file={}".format(self.save_variables(variables))
            )
            success = self.command.sh(
                terraform_command,
                cwd = self.disk.base_path,
                env = self.environment,
                line_prefix = '[terraform]: '
            )
        if not success:
            if not self.command.debug:
                self.clean_project()
            raise TerraformError("Terraform apply failed: {}".format(" ".join(terraform_command)))

        self.command.info('')

        state = self.load_state()

        if not self.command.debug:
            self.clean_project()
        return state


    def destroy(self, variables, state):
        self.clean_project()
        self.save_state(state)

        with self.thread_lock:
            self.init()

            terraform_command = [
                'terraform',
                'destroy',
                '-auto-approve',
                "-var-file={}".format(self.save_variables(variables))
            ]
            success = self.command.sh(
                terraform_command,
                cwd = self.disk.base_path,
                env = self.environment,
                line_prefix = '[terraform]: '
            )
        if not self.command.debug:
            self.clean_project()

        if not success:
            raise TerraformError("Terraform destroy failed: {}".format(" ".join(terraform_command)))


    def save_variables(self, variables):
        return self.disk.save(dump_json(variables, indent = 2), TERRAFORM_VARS_FILE)


    def save_state(self, state):
        return self.disk.save(dump_json(state, indent = 2), TERRAFORM_STATE_FILE)

    def load_state(self):
        return load_json(self.disk.load(TERRAFORM_STATE_FILE))


    def clean_project(self):
        for file in (
            '.terraform',
            '.terraform.lock.hcl',
            TERRAFORM_VARS_FILE,
            TERRAFORM_STATE_FILE,
            "{}.backup".format(TERRAFORM_STATE_FILE)
        ):
            self.disk.remove(file)
