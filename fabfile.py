from fusionbox.fabric_helpers import *

env.roledefs = {
        'dev': ['dev.fusionbox.com'],
        }

env.project_name = 'django-widgy'
env.short_name = 'widgy'
env.tld = ''


def stage_with_docs(pip=False, migrate=False, syncdb=False, branch=None):
    stage(pip=pip, migrate=migrate, syncdb=syncdb, branch=branch)
    with cd('/var/www/%s%s/doc' % (env.project_name, env.tld)):
        with virtualenv(env.short_name):
            run("make html")

stage = roles('dev')(stage)
dstage = roles('dev')(stage_with_docs)
