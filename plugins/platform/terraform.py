from systems.plugins.index import BaseProvider
from utility.data import dump_json
from utility.terraform import Terraform


class Provider(BaseProvider('platform', 'terraform')):

    def initialize_terraform(self, instance):
        if not getattr(self, 'terraform', False):
            self.terraform = Terraform(
                self.command,
                instance.name,
                self.get_path(instance),
                instance.environment
            )


    def get_variables(self, instance):
        config = self.get_config(instance)
        return config.get('values', {})


    def provision_platform(self, instance, repository):
        print('provisioning terraform')
        print(repository.disk.base_path)
        print(dump_json(self.get_config(instance), indent = 2))

        # self.initialize_terraform(instance)
        # if self.test:
        #     self.plan(instance)
        # else:
        #     self.apply(instance)

    def destroy_platform(self, instance, repository):
        print('finalizing terraform')
        print(repository.disk.base_path)
        print(dump_json(self.get_config(instance), indent = 2))

        # self.initialize_terraform(instance)
        # self.destroy(instance)


    def plan(self, instance):
        variables = self.get_variables(instance)
        self.command.data('variables', dump_json(variables, indent = 2))
        self.terraform.plan(variables, instance.state)

    def apply(self, instance):
        variables = self.get_variables(instance)
        if self.command.debug:
            self.command.notice("{}: {}".format(
                instance.name,
                dump_json(variables, indent = 2)
            ))
        instance.state = self.terraform.apply(variables, instance.state)

    def destroy(self, instance):
        variables = self.get_variables(instance)
        if self.command.debug:
            self.command.notice("{}: {}".format(
                instance.name,
                dump_json(variables, indent = 2)
            ))
        self.terraform.destroy(variables, instance.state)
