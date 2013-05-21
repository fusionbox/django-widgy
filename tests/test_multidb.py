import os

from test_sqlite import *

engine = os.getenv('DATABASE_ENGINE')
if engine == 'mysql':
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "widgy",
            "USER": "root",
            "PASSWORD": "",
            "HOST": "",
        }
    }
elif engine == 'postgres':
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "widgy",
            "USER": "postgres",
        }
    }
elif engine == 'sqlite':
    pass
elif engine:
    assert False, "%r is not a valid DATABASE_ENGINE" % engine
