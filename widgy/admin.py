from django.contrib.admin import ModelAdmin
from widgy.forms import WidgyFormMixin


class WidgyAdmin(ModelAdmin):
    """
    Model Admin for models which will have a widgy tree under them
    """
    def get_form(self, request, obj=None, **kwargs):
        form = super(WidgyAdmin, self).get_form(request, obj, **kwargs)

        if not issubclass(form, WidgyAdmin):
            class form(WidgyFormMixin, form):
                pass

        return form
