import mock

from django.test import TestCase
from django.utils.unittest import skipUnless
from django.test.client import RequestFactory
from django import forms
from django.conf import settings

from widgy.site import WidgySite
from widgy.utils import get_user_model

User = get_user_model()
widgy_site = WidgySite()

FORM_BUILDER_INSTALLED = 'widgy.contrib.form_builder' in settings.INSTALLED_APPS

if FORM_BUILDER_INSTALLED:
    from widgy.contrib.form_builder.models import Form, FormInput
    from widgy.contrib.widgy_mezzanine.views import handle_form


@skipUnless(FORM_BUILDER_INSTALLED, 'form_builder not installed')
class TestFormHandler(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.form = Form.add_root(widgy_site)

    def test_get(self):
        req = self.factory.get('/?from=/foo/')
        resp = handle_form(req, form_node_pk=self.form.node.pk)

        self.assertEqual(resp['Location'], '/foo/')

    def test_post(self):
        req = self.factory.post('/?from=/foo/')

        with mock.patch.object(Form, 'execute') as form_execute:
            form_execute.return_value = object()
            resp = handle_form(req, form_node_pk=self.form.node.pk)

        args, kwargs = form_execute.call_args
        self.assertIs(args[0], req)
        self.assertIsInstance(args[1], forms.BaseForm)

        # should use the form's response
        self.assertIs(resp, form_execute.return_value)

    def test_post_rerender(self):
        self.form.children['fields'].add_child(widgy_site, FormInput,
                                               label='foo',
                                               required=True,
                                               type='text',
                                               )

        req = self.factory.post('/?from=/foo/')
        req.user = User(is_superuser=True)

        with mock.patch.object(Form, 'execute') as form_execute:
            with mock.patch('widgy.contrib.widgy_mezzanine.views.page_view') as page_view:
                page_view.return_value = object()
                resp = handle_form(req, form_node_pk=self.form.node.pk)

        form_execute.assert_not_called()

        self.assertIs(resp, page_view.return_value)

        args, kwargs = page_view.call_args
        self.assertIs(args[0], req)
        extra_context = kwargs['extra_context']

        self.assertEqual(extra_context['root_node_override'], self.form.node)

        django_form = extra_context[self.form.context_var]
        self.assertIsInstance(django_form, forms.BaseForm)
        self.assertTrue(django_form.errors)
