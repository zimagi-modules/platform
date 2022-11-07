from django.conf import settings

from systems.plugins.index import BasePlugin
from utility.data import deep_merge
from utility.filesystem import filesystem_dir
from utility.git import Git

import os


class BaseProvider(BasePlugin('platform')):

    @property
    def base_path(self):
        return self.manager.platform_path

    @property
    def filesystem(self):
        return filesystem_dir(self.base_path)

    def get_path(self, instance):
        return os.path.join(self.base_path, instance.name)

    def project(self, instance):
        return filesystem_dir(self.get_path(instance))


    def get_config(self, instance):
        if not getattr(self, '_instance_config', None):
            self._instance_config = {}

        if instance.name not in self._instance_config:
            self._instance_config[instance.name] = deep_merge(instance.config, instance.secrets)
        return self._instance_config[instance.name]


    def initialize_instance(self, instance, created):
        project_path = self.get_path(instance)
        config = self.get_config(instance)
        public_key = config.get('public_key', None)
        private_key = config.get('private_key', None)

        if not os.path.isdir(os.path.join(project_path, '.git')):
            repository = Git.clone(instance.remote, project_path,
                reference = instance.reference,
                private_key = private_key,
                public_key = public_key
            )
            self.command.success("Initialized repository {} from remote {}".format(instance.name, instance.remote))
        else:
            repository = Git(project_path,
                private_key = private_key,
                public_key = public_key
            )
            repository.set_remote('origin', instance.remote)
            repository.pull(
                remote = 'origin',
                branch = instance.reference
            )
            self.command.success("Updated repository {} from remote {}".format(instance.name, instance.remote))

        self.provision_platform(instance, repository)

        self.command.save_instance(self.command._host, instance.name, {
            'host': instance.variables.get(settings.PLATFORM_HOST_VARIABLE),
            'command_port': instance.variables.get(settings.PLATFORM_COMMAND_API_PORT_VARIABLE, 5123),
            'data_port': instance.variables.get(settings.PLATFORM_DATA_API_PORT_VARIABLE, 5323),
            'user': settings.ADMIN_USER,
            'token': settings.DEFAULT_ADMIN_TOKEN,
            'encryption_key': settings.ADMIN_API_KEY
        })


    def provision_platform(self, instance, repository):
        # Override in sub class
        pass


    def finalize_instance(self, instance):
        project_path = self.get_path(instance)
        config = self.get_config(instance)

        if os.path.isdir(project_path):
            repository = Git(project_path,
                private_key = config.get('private_key', None),
                public_key = config.get('public_key', None)
            )
            self.command.remove_instance(self.command._host, instance.name)
            self.destroy_platform(instance, repository)
            repository.disk.delete()

    def destroy_platform(self, instance, repository):
        # Override in sub class
        pass
