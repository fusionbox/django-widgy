from django.test import TestCase
from django import forms

import mock

from modeltests.core_tests.widgy_config import widgy_site
from widgy.contrib.form_builder.models import Form, FormInput, Textarea, FormSubmission, FormField, Uncaptcha


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

        input = self.form.add_child(widgy_site, FormInput)
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


class TestForm(TestCase):
    def make_form(self):
        form = Form.add_root(widgy_site)
        fields = []
        fields.append(form.add_child(widgy_site, FormInput,
                                     label='field 1',
                                     type='text'))
        fields.append(form.add_child(widgy_site, FormInput,
                                     label='field 2',
                                     type='text'))
        fields.append(form.add_child(widgy_site, Textarea,
                                     label='field 3',))
        return form, fields

    def setUp(self):
        self.form, self.fields = self.make_form()

    def submit(self, a, b, c, form=None):
        form = form or self.form
        fields = [i for i in form.get_children() if isinstance(i, FormField)]

        return FormSubmission.objects.submit(
            form=form or self.form,
            data={
                fields[0].get_formfield_name(): a,
                fields[1].get_formfield_name(): b,
                fields[2].get_formfield_name(): c,
            })

    def test_delete_doesnt_delete(self):
        form = Form.add_root(widgy_site)
        input = form.add_child(widgy_site, FormInput)

        form.delete()

        form = Form.objects.get(pk=form.pk)
        self.assertTrue(form.node.is_root())
        self.assertIn(input, form.get_children())

    def test_as_dict(self):
        submission = self.submit('a', 'b', 'c')
        expected = {
            self.fields[0].ident: 'a',
            self.fields[1].ident: 'b',
            self.fields[2].ident: 'c',
        }
        self.assertEqual(expected, submission.as_dict())

    def test_field_names(self):
        self.submit('a', 'b', 'c')
        self.assertEqual(FormSubmission.objects.field_names(), {
            self.fields[0].ident: 'field 1',
            self.fields[1].ident: 'field 2',
            self.fields[2].ident: 'field 3',
        })

        self.fields[0].label = 'field 1 edited'
        self.fields[0].save()

        self.submit('a', 'b', 'c')

        self.assertEqual(FormSubmission.objects.field_names(), {
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

        self.assertEqual(FormSubmission.objects.field_names(), {
            ident: 'field 1',
            self.fields[1].ident: 'field 2',
            self.fields[2].ident: 'field 3',
        })

    def test_as_dictionaries(self):
        self.submit('a', 'b', 'c')
        self.submit('1', '2', '3')

        self.assertEqual([sorted(i.values()) for i in FormSubmission.objects.as_dictionaries()],
                         [sorted(['a', 'b', 'c']), sorted(['1', '2', '3'])])

    def test_parent_form(self):
        for field in self.fields:
            self.assertEqual(field.parent_form, self.form)

    def test_with_versioning(self):
        new_form = self.form.node.clone_tree(freeze=False).content

        self.submit('a', 'b', 'c')

        f = [i for i in new_form.get_children() if hasattr(i, 'label') and i.label == 'field 1'][0]
        f.label = 'updated'
        f.save()

        self.submit('1', '2', '3', form=new_form)

        self.assertEqual(new_form.submission_count, 2)
        self.assertEqual(new_form.submissions.field_names(), {
            self.fields[0].ident: 'updated',
            self.fields[1].ident: 'field 2',
            self.fields[2].ident: 'field 3',
        })

    def test_serialize_value(self):
        with mock.patch('widgy.contrib.form_builder.models.Textarea.serialize_value') as serialize:
            serialize.return_value = 'serialize.return_value'

            submission = self.submit('1', '2', '3')

        serialize.assert_called_with('3')

        self.assertEqual(submission.as_dict(), {
            self.fields[0].ident: '1',
            self.fields[1].ident: '2',
            self.fields[2].ident: serialize.return_value,
        })
