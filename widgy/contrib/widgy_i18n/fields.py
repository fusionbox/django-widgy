from django.conf import settings
from django.db import models


class LanguageCodeField(models.CharField):
    """
    A CharField whose choices are the project's ``settings.LANGUAGES``.

    The choices are applied at runtime (forms, admin, validation) but are
    hidden from migrations. They differ per project and per Django version
    and have no effect on the database, so recording them would make every
    project, and every Django upgrade, generate a new migration for this app.

    For the same reason the field deconstructs as a plain ``CharField``:
    migrations never need to import this class.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 10)
        kwargs['choices'] = settings.LANGUAGES
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop('choices', None)
        return name, 'django.db.models.CharField', args, kwargs
