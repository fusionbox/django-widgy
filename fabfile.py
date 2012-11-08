from fusionbox.fabric_helpers import *

env.roledefs = {
        'dev': ['dev.fusionbox.com'],
        }

env.project_name = 'django-widgy'
env.short_name = 'widgy'
env.tld = ''


_stage = stage
def stage(pip=False, migrate=False, syncdb=False, branch=None):
    _stage(pip=pip, migrate=migrate, syncdb=syncdb, branch=branch)
    with cd('/var/www/%s%s/doc' % (env.project_name, env.tld)):
        with virtualenv(env.short_name):
            run("make html")

stage = roles('dev')(stage)
