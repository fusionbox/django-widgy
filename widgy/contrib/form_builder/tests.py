"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django import forms

from modeltests.core_tests.widgy_config import widgy_site
from widgy.contrib.form_builder.models import Form, FormInput


class GetFormTest(TestCase):
    def setUp(self):
        self.form = Form.add_root(widgy_site)

    def test_get_form(self):
        input1 = self.form.add_child(widgy_site, FormInput)
        input1.type = 'text'
        input1.label = 'Test'
        input1.save()

        input2 = self.form.add_child(widgy_site, FormInput)
        input2.type = 'text'
        input2.label = 'Test 2'
        input2.save()

        form_class = self.form.get_form()

        data = {
            input1.get_formfield_name(): 'foo',
            input2.get_formfield_name(): 'bar',
        }

        f = form_class(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data, data)

    def test_get_formfield(self):
        self.form = Form.add_root(widgy_site)

        input = self.form.add_child(widgy_site, FormInput)
        input.type = 'text'
        input.label = 'Test'
        input.save()

        field = input.get_formfield()

        self.assertTrue(isinstance(field, forms.CharField))
        self.assertEqual(field.label, 'Test')
