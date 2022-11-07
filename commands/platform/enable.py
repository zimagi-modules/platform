from systems.commands.index import Command


class Enable(Command('platform.enable')):

    def exec(self):
        self.platform # Check if platform exists
        self.save_instance(self._platform, self.platform_key, {
            'config__values__active': True
        })
