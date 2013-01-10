from django.contrib.admin import ModelAdmin
from widgy.forms import WidgyFormMixin


class WidgyAdmin(ModelAdmin):
    """
    Abstract base class for ModelAdmins whose models contain WidgyFields.
    """
    # You must provide a site when declaring your WidgyAdmin
    # site = None

    def get_form(self, request, obj=None, **kwargs):
        form = super(WidgyAdmin, self).get_form(request, obj, **kwargs)

        if not issubclass(form, WidgyAdmin):
            class form(WidgyFormMixin, form):
                site = self.site

        return form
