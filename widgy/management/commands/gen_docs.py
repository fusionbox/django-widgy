import subprocess
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create Sphinx documentation'

    def handle(self, *args, **options):
        try:
            subprocess.check_call(['make', 'html'],
                                  cwd=os.path.join(settings.PROJECT_PATH,
                                                   '..', 'doc'))
        except subprocess.CalledProcessError as e:
            raise CommandError(e)
