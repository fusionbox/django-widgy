from django.utils.importlib import import_module
from django.core.management.templates import TemplateCommand
from django.core.management.base import CommandError


class Command(TemplateCommand):
    help = 'Create a new widgy plugin.'

    def handle(self, app_name=None, target=None, **options):
        if app_name is None:
            raise CommandError("you must provide an app name")

        # Check that the app_name cannot be imported.
        try:
            import_module(app_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing "
                               "Python module and cannot be used as an app "
                               "name. Please try another name." % app_name)

        super(Command, self).handle('plugin', app_name, target, **options)
