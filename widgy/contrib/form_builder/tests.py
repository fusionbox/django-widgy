from __future__ import unicode_literals

import contextlib
import unittest
import uuid

from six.moves import StringIO

from django.test import TestCase
from django.test.client import RequestFactory
from django import forms
from django.utils import timezone
from django.utils.encoding import force_text
from django.core import mail
from django.db import connection
from django.core.files.base import ContentFile

import mock

from widgy.contrib.form_builder.forms import PhoneNumberField
from widgy.contrib.form_builder.models import (
    Form, FormInput, Textarea, FormSubmission, FormField, Uncaptcha,
    EmailUserHandler, EmailSuccessHandler, FileUpload, friendly_uuid
)
from widgy.exceptions import ParentChildRejection
from widgy.utils import build_url
from widgy.models import VersionTracker
from widgy.site import WidgySite

widgy_site = WidgySite()


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

    def test_widget(self):
        self.form = Form.add_root(widgy_site)

        field_widget = self.form.children['fields'].add_child(widgy_site, FormInput,
                                                              type='checkbox',
                                                              label='Test',
                                                              )
        field = field_widget.get_formfield()

        self.assertTrue(isinstance(field.widget, forms.CheckboxInput))

    def test_with_uncaptcha(self):
        uncaptcha = self.form.children['fields'].add_child(widgy_site, Uncaptcha)
        form_class = self.form.build_form_class()
        self.assertTrue(hasattr(form_class, 'clean_%s' % uncaptcha.get_formfield_name()))


@contextlib.contextmanager
def mock_now():
    now = timezone.now().replace(microsecond=0) # mysql only has second precision
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

    def test_friendly_uuid_python2_python3_plays_nice(self):
        """
        Regression test for friendly UUID.

        friendly_uuid should return unicode for comparison with
        values from a request.
        """

        test_uuid = uuid.UUID('{12345678-1234-5678-1234-567812345678}')
        short_uuid = friendly_uuid(test_uuid)
        assert short_uuid == '3cvd8mz9'

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
        field_names = FormSubmission.objects.get_formfield_labels()
        field_names.pop('created_at')
        self.assertEqual(field_names, {
            self.fields[0].ident: 'field 1',
            self.fields[1].ident: 'field 2',
            self.fields[2].ident: 'field 3',
        })

        self.fields[0].label = 'field 1 edited'
        self.fields[0].save()

        self.submit('a', 'b', 'c')

        field_names = FormSubmission.objects.get_formfield_labels()
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

        field_names = FormSubmission.objects.get_formfield_labels()
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

        # Mysql doesn't have millisecond precision for DateTimes, so refetch
        # these objects to portably do it.
        letters = FormSubmission.objects.get(pk=letters.pk)
        numbers = FormSubmission.objects.get(pk=numbers.pk)

        self.assertEqual(letters.as_dict(), letters_dict)
        self.assertEqual(numbers.as_dict(), numbers_dict)

    @unittest.skipIf(connection.vendor == 'mysql',
                     "must have millisecond DateTime precision to order form submissions")
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

        self.assertEqual(list(letters_dict.keys()), field_name_order)
        self.assertEqual(list(letters_dict.values()), [first, 'c', 'a', 'b'])
        self.assertEqual(list(numbers_dict.values()), [second, '3', '1', '2'])

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
        field_names = new_form.submissions.get_formfield_labels()
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

    def test_serialize_file_field(self):
        form = Form.add_root(widgy_site)
        file_field = form.children['fields'].add_child(widgy_site, FileUpload,
                                                       required=False)

        FormSubmission.objects.submit(form=form, data={
            file_field.get_formfield_name(): ContentFile(b'foobar', name='asdf.txt'),
        })

        FormSubmission.objects.submit(form=form, data={
            file_field.get_formfield_name(): None,
        })

        serialized_values = [s[file_field.ident] for s in form.submissions.as_dictionaries()]

        self.assertEqual(serialized_values, [
            '/media/form-uploads/asdf.txt',
            '',
        ])

    def test_csv_unicode(self):
        f = self.fields[0]
        f.label = '\N{INTERROBANG}'
        f.save()

        with mock_now() as now:
            self.submit('\N{SNOWMAN}', '2', '3')

        csv_output = StringIO()
        self.form.submissions.to_csv(csv_output)

        self.assertEqual(force_text(csv_output.getvalue()), (
            "Created at,\N{INTERROBANG},field 2,field 3\r\n"
            "%s,\N{SNOWMAN},2,3\r\n" % (now,))
        )


class TestFormHandler(TestCase):
    def setUp(self):
        self.form = form = Form.add_root(widgy_site)

        self.to_field = to_field = form.children['fields'].add_child(widgy_site, FormInput)
        to_field.type = 'email'
        to_field.save()

        self.email_handler = email_handler = form.children['meta'].children['handlers'].add_child(widgy_site, EmailUserHandler)
        email_handler.to_ident = to_field.ident
        email_handler.save()

    def test_email_success_handler(self):
        self.email_handler.execute(*self.get_execute_args(self.form, {
            self.to_field.get_formfield_name(): '1@example.com',
        }))

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, ['1@example.com'])

    def test_admin_email_success_handler(self):
        email_handler = self.form.children['meta'].children['handlers'].add_child(widgy_site, EmailSuccessHandler)
        email_handler.to = '2@example.com'
        email_handler.save()

        email_handler.execute(*self.get_execute_args(self.form, {
            self.to_field.get_formfield_name(): 'ignore@example.com',
        }))

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, ['2@example.com'])

    def test_email_success_handler_include_attachments(self):
        email_handler = self.form.children['meta'].children['handlers'].add_child(widgy_site, EmailSuccessHandler)
        email_handler.to = '2@example.com'
        email_handler.save()

        request, form_obj = self.get_execute_args(self.form, {
            self.to_field.get_formfield_name(): 'ignored@example.com',
        })
        form_obj.cleaned_data['file'] = ContentFile('foobar', name='asdf.txt')
        email_handler.execute(request, form_obj)

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].attachments, [
            ('asdf.txt', 'foobar', None),
        ])

    def test_email_success_handler_to_pointer_works_after_being_committed(self):
        tracker = VersionTracker.objects.create(working_copy=self.form.node)
        tracker.commit()

        form = tracker.head.root_node.content
        email_handler = [i for i in form.depth_first_order() if isinstance(i, EmailUserHandler)][0]
        to_field = [i for i in form.depth_first_order() if isinstance(i, FormInput)][0]

        form_obj = form.build_form_class()({
            to_field.get_formfield_name(): '1@example.com',
        })
        assert form_obj.is_valid()
        self.assertEqual(email_handler.get_to_emails(form_obj), ['1@example.com'])

    def test_email_success_handler_pre_delete(self):
        from django.db.models import ProtectedError
        self.assertRaises(ProtectedError, self.to_field.delete)

    def test_email_success_handler_handles_blank_to_attr(self):
        email_handler = self.form.children['meta'].children['handlers'].add_child(widgy_site, EmailSuccessHandler)
        email_handler.to = ''
        email_handler.save()

        self.assertEquals(email_handler.get_to_emails(self.form), [])

    def get_execute_args(self, form, data):
        request_factory = RequestFactory()
        request = request_factory.post(build_url('/', **{'from': '/'}), data)
        form_obj = form.build_form_class()(request.POST)

        assert form_obj.is_valid()
        return request, form_obj

    def test_post_create_autofill(self):
        email_handler2 = self.form.children['meta'].children['handlers'].add_child(widgy_site, EmailUserHandler)
        self.assertEqual(email_handler2.to_ident, self.to_field.ident)


class TestFormCompatibility(TestCase):
    @unittest.expectedFailure
    def test_uncaptcha_compatibility(self):
        form = Form.add_root(widgy_site)
        fields = form.children['fields']
        fields.add_child(widgy_site, Uncaptcha)

        assert not Uncaptcha.valid_child_of(fields)
        self.assertRaises(ParentChildRejection, fields.add_child, widgy_site, Uncaptcha)


class TestPhoneNumberField(TestCase):
    def test_good_phone_number(self):
        self.assertEqual(PhoneNumberField().clean('13035555555'), '(303) 555-5555')

    def test_bad_phone_number(self):
        with self.assertRaises(forms.ValidationError):
            PhoneNumberField().clean('978121')

    def test_phone_number_with_good_extension(self):
        self.assertEqual(PhoneNumberField().clean('13035555555ex555555'),
            '(303) 555-5555 ext. 555555')

    def test_phone_number_with_bad_extension(self):
        with self.assertRaises(forms.ValidationError):
            PhoneNumberField().clean('13035555555ex1BAD')

    def test_international_phone_number(self):
        self.assertEqual(PhoneNumberField().clean('+4991319402813'),
            '+49 9131 9402813')

    def test_string_in_phone_number(self):
        with self.assertRaises(forms.ValidationError):
            PhoneNumberField().clean('BADNUMBER')

    def test_phone_number_extension_error(self):
        with self.assertRaises(forms.ValidationError):
            PhoneNumberField(allow_extension=False).clean('13035555555ex123')
