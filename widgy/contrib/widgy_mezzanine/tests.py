import mock
import datetime

from django.test import TestCase
from django.utils.unittest import skipUnless
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from mezzanine.core.models import (CONTENT_STATUS_PUBLISHED,
                                   CONTENT_STATUS_DRAFT)

from widgy.site import WidgySite
from widgy.utils import get_user_model
from widgy.contrib.widgy_mezzanine import get_widgypage_model
from widgy.contrib.widgy_mezzanine.views import ClonePageView, UnpublishView

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

REVIEW_QUEUE_INSTALLED = 'widgy.contrib.review_queue' in settings.INSTALLED_APPS

if REVIEW_QUEUE_INSTALLED:
    from widgy.contrib.review_queue.models import ReviewedVersionCommit, ReviewedVersionTracker
    from widgy.contrib.review_queue.site import ReviewedWidgySite


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
class PageSetup(object):
    def setUp(self):
        super(PageSetup, self).setUp()
        self.factory = RequestFactory()

        self.page = WidgyPage.objects.create(
            root_node=widgy_site.get_version_tracker_model().objects.create(
                working_copy=Button.add_root(widgy_site, text='buttontext').node,
            ),
            title='titleabc',
            slug='slugabc',
        )


class AdminView(PageSetup):
    def as_view(self, **kwargs):
        kwargs.setdefault('has_permission', lambda req: True)
        return self.view_cls.as_view(**kwargs)

    def test_permissions(self):
        with self.assertRaises(PermissionDenied):
            forbid_everything = lambda req: False
            req = self.factory.get('/')
            self.as_view(has_permission=forbid_everything)(req, str(self.page.pk))


class TestClonePage(AdminView, TestCase):
    view_cls = ClonePageView

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


class TestUnpublish(AdminView, TestCase):
    view_cls = UnpublishView

    def test_unpublish(self):
        self.assertEqual(self.page.status, CONTENT_STATUS_PUBLISHED)

        view = self.as_view()
        resp = view(self.factory.get('/'), str(self.page.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.page.title, resp.rendered_content)

        with mock.patch('django.contrib.messages.success') as success_mock:
            req = self.factory.post('/')
            resp = view(req, str(self.page.pk))
        self.assertEqual(resp.status_code, 302)
        success_mock.assert_called_with(req, mock.ANY)

        self.page = WidgyPage.objects.get(pk=self.page.pk)
        self.assertEqual(self.page.status, CONTENT_STATUS_DRAFT)


def refetch(obj):
    return obj.__class__.objects.get(pk=obj.pk)


@skipUnless(REVIEW_QUEUE_INSTALLED, 'review_queue is not installed')
@override_settings(WIDGY_MEZZANINE_SITE=ReviewedWidgySite())
class TestPublicationCommitHandling(PageSetup, TestCase):
    def setUp(self):
        super(TestPublicationCommitHandling, self).setUp()

        from widgy.contrib.widgy_mezzanine.admin import publish_page_on_approve
        self.signal = publish_page_on_approve
        self.user = User.objects.create_superuser(
            username='asfd', password='asdfasdf', email='asdf@example.com',
        )

        self.vt = ReviewedVersionTracker.objects.get(pk=self.page.root_node.pk)

    def test_publish_on_commit(self):
        self.page.status = CONTENT_STATUS_DRAFT
        self.page.save()

        commit = self.vt.commit()
        commit.publish_at = timezone.now() + datetime.timedelta(days=1)

        self.signal(ReviewedVersionCommit, commit, True)
        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_DRAFT)

        commit.approve(self.user)
        self.signal(ReviewedVersionCommit, commit, True)
        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)
        self.assertEqual(refetch(self.page).publish_date, refetch(commit).publish_at)

    def test_committing_again_does_nothing(self):
        self.page.status = CONTENT_STATUS_DRAFT
        commit = self.vt.commit()
        commit.approve(self.user)
        self.signal(ReviewedVersionCommit, commit, True)
        original_publish_date = refetch(self.page).publish_date

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)
        c2 = self.vt.commit(publish_at=timezone.now() + datetime.timedelta(days=1))
        self.signal(ReviewedVersionCommit, c2, True)

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)
        self.assertEqual(refetch(self.page).publish_date, original_publish_date)

    def test_publish_commit_moves_publish_date_up(self):
        self.page.publish_date = timezone.now() + datetime.timedelta(days=1)
        self.page.save()

        commit = self.vt.commit()
        commit.approve(self.user)
        self.signal(ReviewedVersionCommit, commit, True)
        self.assertEqual(refetch(self.page).publish_date, refetch(commit).publish_at)

    def test_unapprove_commit_unpublishes_page_when_there_are_no_other_published_commits(self):
        commit = self.vt.commit()
        commit.approve(self.user)
        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)

        commit.unapprove(self.user)
        self.signal(ReviewedVersionCommit, commit, False)

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_DRAFT)

    def test_unapprove_commit_corrects_publish_date_there_is_another_commit(self):
        c1 = self.vt.commit()
        c1.approve(self.user)

        c2 = self.vt.commit(publish_at=timezone.now() + datetime.timedelta(days=1))
        c2.approve(self.user)
        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)

        c1.unapprove(self.user)
        self.signal(ReviewedVersionCommit, c1, False)

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)
        self.assertEqual(refetch(self.page).publish_date, refetch(c2).publish_at)
