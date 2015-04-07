from __future__ import absolute_import

from django.test import TestCase
from django.test.client import RequestFactory
from django import forms
from django.contrib.contenttypes.models import ContentType

from ..widgy_config import widgy_site
from ..models import (
    VariegatedFieldsWidget, VerboseNameLayout,
    VerboseNameLayoutChild, WidgetWithHTMLHelpText,
)

from widgy.widgets import DateTimeWidget, DateWidget, TimeWidget
from widgy.forms import WidgyFormField


factory = RequestFactory()


class TestFormCreation(TestCase):
    def test_field_with_choices(self):
        widget = VariegatedFieldsWidget.add_root(widgy_site)
        form_class = widget.get_form_class(request=None)()
        self.assertIsInstance(form_class.fields['color'].widget, forms.Select)

    def test_date_fields(self):
        widget = VariegatedFieldsWidget.add_root(widgy_site)
        form_class = widget.get_form_class(request=None)()

        self.assertIsInstance(form_class.fields['date'].widget, DateWidget)
        self.assertIsInstance(form_class.fields['time'].widget, TimeWidget)
        self.assertIsInstance(form_class.fields['datetime'].widget, DateTimeWidget)


class TestFieldAsDiv(TestCase):
    def test_field_as_div_allows_html_in_help_text(self):
        widget = WidgetWithHTMLHelpText.add_root(widgy_site)
        request = factory.get('/')
        rendered_form = widget.get_form_template(request)
        self.assertIn('Your<br>Name', rendered_form)


class TestWidgyFormField(TestCase):
    def test_content_type_radio_labels(self):
        ct1 = ContentType.objects.get_for_model(VerboseNameLayout)
        ct2 = ContentType.objects.get_for_model(VerboseNameLayoutChild)

        # Sometimes the ContentType is created and stored in the database and
        # then the developer changes the verbose_name of the model. We model
        # that by retrieving the ContentType objects (which will put them in
        # the database) and then changing the verbose_name.
        VerboseNameLayoutChild._meta.verbose_name = 'barBaz'

        field = WidgyFormField(
            site=widgy_site,
            queryset=ContentType.objects.filter(pk__in=[ct1.pk, ct2.pk]).order_by('pk'),
        )

        # owner can be None because WidgyFormField doesn't use it yet
        field.conform_to_value(owner=None, value=None)

        self.assertSequenceEqual(list(field.widget.choices), sorted([
            (ct1.pk, 'Verbose name layout'),
            (ct2.pk, 'BarBaz'),
        ]))
