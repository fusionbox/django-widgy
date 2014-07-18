import mock

from django.test import TestCase
from django.utils.unittest import skipUnless
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied

from widgy.site import WidgySite
from widgy.utils import get_user_model
from widgy.contrib.widgy_mezzanine import get_widgypage_model
from widgy.contrib.widgy_mezzanine.views import ClonePageView

User = get_user_model()
widgy_site = WidgySite()
WidgyPage = get_widgypage_model()

FORM_BUILDER_INSTALLED = 'widgy.contrib.form_builder' in settings.INSTALLED_APPS

if FORM_BUILDER_INSTALLED:
    from widgy.contrib.form_builder.models import Form, FormInput
    from widgy.contrib.widgy_mezzanine.views import handle_form

PAGE_BUILDER_INSTALLED = 'widgy.contrib.page_builder' in settings.INSTALLED_APPS

if PAGE_BUILDER_INSTALLED:
    from widgy.contrib.page_builder.models import Button
    from widgy.contrib.widgy_mezzanine.views import PreviewView


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

    @override_settings(MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES + (
        'mezzanine.pages.middleware.PageMiddleware',
    ))
    def test_post_no_404(self):
        """
        Mezzanine==3.1.2 introduced a change that caused calls to page view
        (such as in the form_invalid of the handle_form view to 404.  This test
        ensures that there is no 404.
        """
        from widgy.contrib.widgy_mezzanine.models import WidgyPage
        page = WidgyPage.objects.create(title='Test')

        self.form.children['fields'].add_child(widgy_site, FormInput,
                                               label='foo',
                                               required=True,
                                               type='text',
                                               )

        req = self.factory.post('/?from=/foo/')
        req.user = User(is_superuser=True)

        resp = handle_form(req, form_node_pk=self.form.node.pk, slug=page.slug)

        self.assertEqual(resp.status_code, 200)


@skipUnless(PAGE_BUILDER_INSTALLED, 'page_builder is not installed')
@override_settings(MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES + (
    'mezzanine.pages.middleware.PageMiddleware',
))
class TestPreviewView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.preview_view = PreviewView.as_view(site=widgy_site)
        self.request = self.factory.get('/')
        self.request.user = User(is_superuser=True)

    def test_preview(self):
        page = WidgyPage.objects.create(title='Test')
        root_node1 = Button.add_root(widgy_site, text='Test 1')
        root_node2 = Button.add_root(widgy_site, text='Test 2')

        resp1 = self.preview_view(self.request, node_pk=root_node1.node.pk, slug=page.slug)

        self.assertEqual(resp1.status_code, 200)
        self.assertIn('Test 1', resp1.rendered_content)
        self.assertEqual(resp1.context_data['page'].get_content_model(), page)

        resp2 = self.preview_view(self.request, node_pk=root_node2.node.pk, slug=page.slug)

        self.assertEqual(resp2.status_code, 200)
        self.assertIn('Test 2', resp2.rendered_content)

    def test_preview_without_page(self):
        button = Button.add_root(widgy_site, text='Button text')

        resp = self.preview_view(self.request, node_pk=button.node.pk)
        self.assertIn(button.text, resp.rendered_content)


@skipUnless(PAGE_BUILDER_INSTALLED, 'page_builder is not installed')
class TestClonePage(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.page = WidgyPage.objects.create(
            root_node=widgy_site.get_version_tracker_model().objects.create(
                working_copy=Button.add_root(widgy_site, text='buttontext').node,
            ),
            title='titleabc',
            slug='slugabc',
        )

    def as_view(self, **kwargs):
        kwargs.setdefault('has_permission', lambda req: True)
        return ClonePageView.as_view(**kwargs)

    def test_permissions(self):
        with self.assertRaises(PermissionDenied):
            forbid_everything = lambda req: False
            req = self.factory.get('/')
            self.as_view(has_permission=forbid_everything)(req, str(self.page.pk))

    def test_get(self):
        view = self.as_view()

        resp = view(self.factory.get('/'), str(self.page.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.page.title, resp.rendered_content)
        self.assertNotIn(self.page.slug, resp.rendered_content)

    def test_post(self):
        view = self.as_view()
        with mock.patch('django.contrib.messages.success') as success_mock:
            req = self.factory.post('/', {'title': 'new title'})

            view(req, str(self.page.pk))

        new_page = WidgyPage.objects.exclude(pk=self.page.pk).get()

        success_mock.assert_called_with(req, mock.ANY)
        success_message = success_mock.call_args[0][1]
        self.assertIn(self.page.title, success_message)
        self.assertIn(new_page.title, success_message)

        self.assertNotEqual(new_page.slug, self.page.slug)
        self.assertEqual(new_page.title, 'new title')

        self.assertEqual(new_page.root_node.working_copy.content.text, 'buttontext')
