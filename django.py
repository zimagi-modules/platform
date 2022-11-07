from django.conf import settings

from settings.config import Config

#
# Platform configuration
#
settings.PROJECT_PATH_MAP['platform_path'] = 'platforms'

PLATFORM_HOST_VARIABLE = 'zimagi_host'
PLATFORM_COMMAND_API_PORT_VARIABLE = 'zimagi_command_port'
PLATFORM_DATA_API_PORT_VARIABLE = 'zimagi_data_port'

PLATFORM_SSH_HOST_VARIABLE = 'ssh_host'
PLATFORM_SSH_PORT_VARIABLE = 'ssh_port'
PLATFORM_SSH_USER_VARIABLE = 'ssh_user'

#
# Terraform configuration
#
TERRAFORM_MAX_PROCESSES = Config.integer('ZIMAGI_TERRAFORM_MAX_PROCESSES', 10)
