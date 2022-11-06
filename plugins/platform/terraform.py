from systems.plugins.index import BaseProvider
from utility.data import dump_json
from utility.terraform import Terraform


class Provider(BaseProvider('platform', 'terraform')):

    def initialize_terraform(self, instance):
        if not getattr(self, 'terraform', False):
            self.terraform = Terraform(
                self.command,
                instance.name,
                self.get_path(instance)
            )


    def initialize_instance(self, instance, created):
        print('initializing terraform')
        print(dump_json(self.get_config(instance), indent = 2))
        super().initialize_instance(instance, created)

        # self.initialize_terraform(instance)
        # if self.test:
        #     self.plan(instance)
        # else:
        #     self.apply(instance)

    def finalize_instance(self, instance):
        print('finalizing terraform')
        print(dump_json(self.get_config(instance), indent = 2))
        super().finalize_instance(instance)
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
