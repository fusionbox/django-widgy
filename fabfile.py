from fabric.api import roles, env
from fusionbox.fabric import fb_env

from fusionbox.fabric.django import stage, deploy, shell

env.forward_agent = True
env.use_ssh_config = True

env.roledefs = {
        'dev': ['dev.fusionbox.com'],
        #'live': [''],
        }

fb_env.transport_method = 'rsync'
fb_env.project_name = 'django-widgy'
fb_env.virtualenv = 'widgy'
fb_env.vassal = 'widgy'
fb_env.tld = ''

stage = roles('dev')(stage)
#deploy = roles('live')(deploy)
shell = shell
