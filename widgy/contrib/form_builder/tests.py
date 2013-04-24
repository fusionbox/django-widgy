"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from __future__ import unicode_literals

import contextlib

from django.test import TestCase
from django import forms
from django.utils import timezone

import mock

from modeltests.core_tests.widgy_config import widgy_site
from widgy.contrib.form_builder.models import Form, FormInput, Textarea, FormSubmission, FormField, Uncaptcha


class GetFormTest(TestCase):
    def setUp(self):
        self.form = Form.add_root(widgy_site)

    def test_get_form(self):
        input1 = self.form.children['fields'].add_child(widgy_site, FormInput)
        input1.type = 'text'
        input1.label = 'Test'
        input1.save()

        input2 = self.form.children['fields'].add_child(widgy_site, FormInput)
        input2.type = 'text'
        input2.label = 'Test 2'
        input2.save()

        form_class = self.form.build_form_class()

        data = {
            input1.get_formfield_name(): 'foo',
            input2.get_formfield_name(): 'bar',
        }

        f = form_class(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data, data)

    def test_get_formfield(self):
        self.form = Form.add_root(widgy_site)

        input = self.form.children['fields'].add_child(widgy_site, FormInput)
        input.type = 'text'
        input.label = 'Test'
        input.save()

        field = input.get_formfield()

        self.assertTrue(isinstance(field, forms.CharField))
        self.assertEqual(field.label, 'Test')

    def test_with_uncaptcha(self):
        uncaptcha = self.form.add_child(widgy_site, Uncaptcha)
        form_class = self.form.build_form_class()
        self.assertTrue(hasattr(form_class, 'clean_%s' % uncaptcha.get_formfield_name()))


@contextlib.contextmanager
def mock_now():
    now = timezone.now()
    with mock.patch('django.utils.timezone.now') as tz_now:
        tz_now.return_value = now
        yield now


class TestForm(TestCase):
    def make_form(self):
        form = Form.add_root(widgy_site)
        fields = []
        fields.append(form.children['fields'].add_child(widgy_site, FormInput,
                                                        label='field 1',
                                                        type='text'))
        fields.append(form.children['fields'].add_child(widgy_site, FormInput,
                                                        label='field 2',
                                                        type='text'))
        fields.append(form.children['fields'].add_child(widgy_site, Textarea,
                                                        label='field 3',))
        return form, fields

    def setUp(self):
        self.form, self.fields = self.make_form()

    def submit(self, a, b, c, form=None):
        form = form or self.form
        fields = [i for i in form.children['fields'].get_children() if isinstance(i, FormField)]

        return FormSubmission.objects.submit(
            form=form or self.form,
            data={
                fields[0].get_formfield_name(): a,
                fields[1].get_formfield_name(): b,
                fields[2].get_formfield_name(): c,
            })

    def test_delete_doesnt_delete(self):
        form = Form.add_root(widgy_site)
        input = form.children['fields'].add_child(widgy_site, FormInput)

        form.delete()

        form = Form.objects.get(pk=form.pk)
        self.assertTrue(form.node.is_root())
        self.assertIn(input, form.children['fields'].get_children())

    def test_as_dict(self):
        with mock_now() as now:
            submission = self.submit('a', 'b', 'c')
        expected = {
            'created_at': now,
            self.fields[0].ident: 'a',
            self.fields[1].ident: 'b',
            self.fields[2].ident: 'c',
        }
        self.assertEqual(expected, submission.as_dict())

    def test_field_names(self):
        self.submit('a', 'b', 'c')
        field_names = FormSubmission.objects.field_names()
        field_names.pop('created_at')
        self.assertEqual(field_names, {
            self.fields[0].ident: 'field 1',
            self.fields[1].ident: 'field 2',
            self.fields[2].ident: 'field 3',
        })

        self.fields[0].label = 'field 1 edited'
        self.fields[0].save()

        self.submit('a', 'b', 'c')

        field_names = FormSubmission.objects.field_names()
        field_names.pop('created_at')
        self.assertEqual(field_names, {
            self.fields[0].ident: 'field 1 edited',
            self.fields[1].ident: 'field 2',
            self.fields[2].ident: 'field 3',
        })

    def test_prefetch_submission_count(self):
        forms = list(Form.objects.all().annotate_submission_count())
        self.assertEqual(forms[0].submission_count, 0)

        new_form, new_fields = self.make_form()
        self.submit('a', 'b', 'c')
        self.submit('a', 'b', 'c')
        self.submit('a', 'b', 'c', form=new_form)

        forms = list(Form.objects.all().annotate_submission_count())
        self.assertEqual(forms[0].submission_count, 2)
        self.assertEqual(forms[1].submission_count, 1)

        for form in forms:
            self.assertEqual(len(form.submissions), form.submission_count)

    def test_submission_count(self):
        new_form, new_fields = self.make_form()
        self.submit('a', 'b', 'c')
        self.submit('a', 'b', 'c')
        self.submit('a', 'b', 'c', form=new_form)

        forms = list(Form.objects.all())
        for form in forms:
            self.assertEqual(len(form.submissions), form.submission_count)

    def test_name_is_preserved_after_field_is_deleted(self):
        self.submit('a', 'b', 'c')
        ident = self.fields[0].ident
        self.fields[0].delete()

        field_names = FormSubmission.objects.field_names()
        field_names.pop('created_at')
        self.assertEqual(field_names, {
            ident: 'field 1',
            self.fields[1].ident: 'field 2',
            self.fields[2].ident: 'field 3',
        })

    def test_as_dictionaries(self):
        letters = self.submit('a', 'b', 'c')
        numbers = self.submit('1', '2', '3')

        letters_dict, numbers_dict = FormSubmission.objects.as_dictionaries()

        self.assertEqual(letters.as_dict(), letters_dict)
        self.assertEqual(numbers.as_dict(), numbers_dict)

    def test_as_ordered_dictionaries(self):
        with mock_now() as first:
            self.submit('a', 'b', 'c')

        with mock_now() as second:
            self.submit('1', '2', '3')

        field_name_order = [
            'created_at',
            self.fields[2].ident,
            self.fields[0].ident,
            self.fields[1].ident,
        ]

        letters_dict, numbers_dict = list(FormSubmission.objects.as_ordered_dictionaries(field_name_order))

        self.assertEqual(letters_dict.keys(), field_name_order)
        self.assertEqual(letters_dict.values(), [first, 'c', 'a', 'b'])
        self.assertEqual(numbers_dict.values(), [second, '3', '1', '2'])

    def test_parent_form(self):
        for field in self.fields:
            self.assertEqual(field.parent_form, self.form)

    def test_with_versioning(self):
        new_form = self.form.node.clone_tree(freeze=False).content

        self.submit('a', 'b', 'c')

        f = [i for i in new_form.children['fields'].get_children() if hasattr(i, 'label') and i.label == 'field 1'][0]
        f.label = 'updated'
        f.save()

        self.submit('1', '2', '3', form=new_form)

        self.assertEqual(new_form.submission_count, 2)
        field_names = new_form.submissions.field_names()
        field_names.pop('created_at')
        self.assertEqual(field_names, {
            self.fields[0].ident: 'updated',
            self.fields[1].ident: 'field 2',
            self.fields[2].ident: 'field 3',
        })

    def test_serialize_value(self):
        with mock.patch('widgy.contrib.form_builder.models.Textarea.serialize_value') as serialize:
            serialize.return_value = 'serialize.return_value'

            submission = self.submit('1', '2', '3')

        serialize.assert_called_with('3')

        self.assertEqual(submission.as_dict()[self.fields[2].ident], serialize.return_value)
