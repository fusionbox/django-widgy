from fusionbox.fabric_helpers import *

env.roledefs = {
        'dev': ['dev.fusionbox.com'],
        }

env.project_name = 'django-widgy'
env.short_name = 'widgy'
env.tld = ''

stage = roles('dev')(stage)
