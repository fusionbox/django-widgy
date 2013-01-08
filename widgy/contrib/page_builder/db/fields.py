from django.db import models

from widgy.contrib.page_builder.forms import MarkdownField as MarkdownFormField, MarkdownWidget

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^widgy\.contrib\.page_builder\.db\.fields\.MarkdownField"])


class MarkdownField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': MarkdownFormField,
            'widget': MarkdownWidget,
        }

        defaults.update(kwargs)

        return super(MarkdownField, self).formfield(**defaults)
