from django.conf import settings

from systems.commands.index import Command
from utility.data import deep_merge
from utility.temp import temp_dir

import subprocess


class Ssh(Command('platform.ssh')):

    def exec(self):
        platform = self.platform
        config = deep_merge(
            platform.variables,
            platform.secrets
        )
        host = config.get(settings.PLATFORM_SSH_HOST_VARIABLE)
        port = config.get(settings.PLATFORM_SSH_PORT_VARIABLE, 22)
        user = config.get(settings.PLATFORM_SSH_USER_VARIABLE)
        private_key = config.get('private_key')

        self.silent_data('host', host)
        self.silent_data('ssh_port', port)
        self.silent_data('user', user)
        self.silent_data('private_key', private_key)

        if not settings.API_EXEC:
            self._start_session(host, port, user, private_key)

    def postprocess(self, result):
        self._start_session(
            result.get_named_data('host'),
            result.get_named_data('ssh_port'),
            result.get_named_data('user'),
            result.get_named_data('private_key')
        )

    def _start_session(self, host, port, user, private_key):
        with temp_dir() as temp:
            ssh_command = ["ssh -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"]

            ssh_command.append("-i {}".format(
                temp.save("{}\n".format(private_key.strip()), permissions = 0o600)
            ))
            ssh_command.append("-p {}".format(port))
            ssh_command.append("{}@{}".format(user, host))

            subprocess.call(" ".join(ssh_command), shell = True)
