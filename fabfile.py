from fusionbox.fabric_helpers import *

env.roledefs = {
        'dev': ['dev.fusionbox.com'],
        }

env.project_name = 'demo'
env.short_name = 'demo'

stage = roles('dev')(stage)
