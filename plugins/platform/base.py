from systems.plugins.index import BasePlugin
from utility.filesystem import filesystem_dir

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


    def initialize_instance(self, instance, created):
        print('initializing instance')

    def finalize_instance(self, instance):
        print('finalizing instance')
