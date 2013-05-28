from django.test import TestCase
from django import forms
from django.contrib import admin

from modeltests.core_tests.widgy_config import widgy_site
from modeltests.core_tests.models import VariegatedFieldsWidget

from widgy.widgets import DateTimeWidget


class TestFormCreation(TestCase):
    def test_field_with_choices(self):
        widget = VariegatedFieldsWidget.add_root(widgy_site)
        form_class = widget.get_form_class(request=None)()
        self.assertIsInstance(form_class.fields['color'].widget, forms.Select)

    def test_date_fields(self):
        widget = VariegatedFieldsWidget.add_root(widgy_site)
        form_class = widget.get_form_class(request=None)()

        self.assertIsInstance(form_class.fields['date'].widget, admin.widgets.AdminDateWidget)
        self.assertIsInstance(form_class.fields['time'].widget, admin.widgets.AdminTimeWidget)
        self.assertIsInstance(form_class.fields['datetime'].widget, DateTimeWidget)
