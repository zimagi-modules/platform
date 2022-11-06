from django.conf import settings

from settings.config import Config

#
# Module environment configurations
#

#
# Platform configuration
#
settings.PROJECT_PATH_MAP['platform_path'] = 'platforms'

#
# Terraform configuration
#
TERRAFORM_MAX_PROCESSES = Config.integer('ZIMAGI_TERRAFORM_MAX_PROCESSES', 10)
