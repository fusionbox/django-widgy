from django.contrib.admin import ModelAdmin

from widgy.forms import WidgyForm


class WidgyAdmin(ModelAdmin):
    """
    Base class for ModelAdmins whose models contain WidgyFields.
    """
    form = WidgyForm
