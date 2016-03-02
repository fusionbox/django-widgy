from __future__ import absolute_import
import mock
import datetime
from contextlib import contextmanager
from unittest import skipUnless
import uuid

import django
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.core import urlresolvers
from django.contrib.auth.models import Permission, AnonymousUser
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.db.models.signals import post_save
from django.conf.urls import url, include
from django.core.urlresolvers import get_resolver

from mezzanine.core.models import (CONTENT_STATUS_PUBLISHED,
                                   CONTENT_STATUS_DRAFT)
from mezzanine.pages.models import Page

from widgy.site import WidgySite
from widgy.contrib.widgy_mezzanine import get_widgypage_model
from widgy.contrib.widgy_mezzanine.views import ClonePageView, UnpublishView
from widgy.db.fields import get_site

from widgy.contrib.widgy_mezzanine.admin import WidgyPageAdmin

User = get_user_model()
widgy_site = WidgySite()
WidgyPage = get_widgypage_model()

# XXX: Let django import the urlconf module. Django does it smarter
urlpatterns = get_resolver(None).url_patterns
urlpatterns = urlpatterns + [
    url('^widgy_site/', include(widgy_site.urls)),
    url('^accounts/', include('django.contrib.auth.urls')),
]

FORM_BUILDER_INSTALLED = 'widgy.contrib.form_builder' in settings.INSTALLED_APPS

if FORM_BUILDER_INSTALLED:
    from widgy.contrib.form_builder.models import Form, FormInput
    from widgy.contrib.widgy_mezzanine.views import handle_form

PAGE_BUILDER_INSTALLED = 'widgy.contrib.page_builder' in settings.INSTALLED_APPS

if PAGE_BUILDER_INSTALLED:
    from widgy.contrib.page_builder.models import Button, DefaultLayout, MainContent
    from widgy.contrib.widgy_mezzanine.views import PreviewView

REVIEW_QUEUE_INSTALLED = 'widgy.contrib.review_queue' in settings.INSTALLED_APPS

if REVIEW_QUEUE_INSTALLED:
    from widgy.contrib.review_queue.site import ReviewedWidgySite
    reviewed_widgy_site = ReviewedWidgySite()
    urlpatterns += [url('^reviewed_widgy_site/', include(reviewed_widgy_site.urls))]


def make_reviewed(fn):
    """
    Just setting the WIDGY_MEZZANINE_SITE is not enough during tests, because
    WidgyPage.root_node has been set to point to VersionTracker.  We have to
    manually point it to ReviewedVersionTracker.  We do this only in tests
    because on a normal run, you are never going to be changing what models a
    ForeignKey points to (I would hope).
    """
    from widgy.contrib.widgy_mezzanine.admin import publish_page_on_approve

    site = reviewed_widgy_site
    rel = WidgyPage._meta.get_field('root_node').rel
    old_model = rel.model
    dispatch_uid = str(uuid.uuid4())

    fn = override_settings(WIDGY_MEZZANINE_SITE=site)(fn)
    fn = skipUnless(REVIEW_QUEUE_INSTALLED, 'review_queue is not installed')(fn)

    def up():
        # BBB Django 1.8 compatiblity
        if django.VERSION < (1, 9):
            rel.to = site.get_version_tracker_model()
        else:
            rel.model = site.get_version_tracker_model()
        post_save.connect(publish_page_on_approve,
                          sender=site.get_version_tracker_model().commit_model,
                          dispatch_uid=dispatch_uid)

    def down():
        # BBB Django 1.8 compatiblity
        if django.VERSION < (1, 9):
            rel.to = old_model
        else:
            rel.model = old_model
        post_save.disconnect(dispatch_uid=dispatch_uid)

    if isinstance(fn, type):
        old_pre_setup = fn._pre_setup
        old_post_teardown = fn._post_teardown

        def _pre_setup(self):
            up()
            old_pre_setup(self)

        def _post_teardown(self):
            old_post_teardown(self)
            down()

        fn._pre_setup = _pre_setup
        fn._post_teardown = _post_teardown

        return fn
    else:
        def change_foreign_key(*args, **kwargs):
            up()
            try:
                return fn(*args, **kwargs)
            finally:
                down()
        return change_foreign_key


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


class UserSetup(object):
    def setUp(self):
        super(UserSetup, self).setUp()
        self.superuser = User.objects.create_superuser('superuser', 'test@example.com', 'password')
        self.staffuser = User.objects.create_user('staffuser', 'test@example.com', 'password')
        self.staffuser.is_staff = True
        self.staffuser.save()
        self.staffuser.user_permissions = Permission.objects.filter(
            content_type__app_label__in=['pages', 'widgy_mezzanine', 'review_queue', 'page_builder']
        ).exclude(codename='change_reviewedversioncommit')

    @contextmanager
    def as_user(self, username):
        self.client.login(username=username, password='password')
        yield
        self.client.logout()


@skipUnless(PAGE_BUILDER_INSTALLED, 'page_builder is not installed')
@override_settings(MIDDLEWARE_CLASSES=settings.MIDDLEWARE_CLASSES + (
    'mezzanine.pages.middleware.PageMiddleware',
))
class TestPreviewView(UserSetup, TestCase):
    urls = 'widgy.contrib.widgy_mezzanine.tests.test_core'

    def setUp(self):
        super(TestPreviewView, self).setUp()
        self.factory = RequestFactory()
        self.preview_view = PreviewView.as_view(site=widgy_site)
        self.request = self.factory.get('/')
        self.request.user = User(is_superuser=True, is_staff=True)

    def test_preview(self):
        page = WidgyPage.objects.create(title='Test')
        root_node1 = Button.add_root(widgy_site, text='Test 1')
        root_node2 = Button.add_root(widgy_site, text='Test 2')

        resp1 = self.preview_view(self.request, node_pk=root_node1.node.pk, page_pk=page.pk)

        self.assertEqual(resp1.status_code, 200)
        self.assertIn('Test 1', resp1.rendered_content)
        self.assertEqual(resp1.context_data['page'].get_content_model(), page)

        resp2 = self.preview_view(self.request, node_pk=root_node2.node.pk, page_pk=page.pk)

        self.assertEqual(resp2.status_code, 200)
        self.assertIn('Test 2', resp2.rendered_content)

    def test_preview_without_page(self):
        button = Button.add_root(widgy_site, text='Button text')

        resp = self.preview_view(self.request, node_pk=button.node.pk)
        self.assertIn(button.text, resp.rendered_content)

    def test_legacy_url(self):
        page = WidgyPage.objects.create(title='Foo')
        root_node = Button.add_root(widgy_site, text='Foo').node
        with self.as_user('superuser'):
            r = self.client.get(urlresolvers.reverse(
                'widgy.contrib.widgy_mezzanine.views.preview',
                kwargs={'slug': page.slug, 'node_pk': root_node.pk}
            ))
            self.assertRedirects(
                response=r,
                expected_url= urlresolvers.reverse(
                    'widgy.contrib.widgy_mezzanine.views.preview',
                    kwargs={'page_pk': page.pk, 'node_pk': root_node.pk}
                ),
                status_code=301,
            )

    def test_redirects_to_login(self):
        """
        Unauthenticated users trying to preview should be redirected to the login page.
        """

        button = Button.add_root(widgy_site, text='Button text')
        request = self.factory.get('/')
        request.user = AnonymousUser()
        resp = self.preview_view(request, node_pk=button.node.pk)
        self.assertEqual(resp['Location'], urlresolvers.reverse('login') + '?next=' + request.get_full_path())


@skipUnless(PAGE_BUILDER_INSTALLED, 'page_builder is not installed')
class PageSetup(object):
    def setUp(self):
        super(PageSetup, self).setUp()
        self.factory = RequestFactory()

        self.widgy_site = get_site(getattr(settings, 'WIDGY_MEZZANINE_SITE', widgy_site))

        self.page = WidgyPage.objects.create(
            root_node=self.widgy_site.get_version_tracker_model().objects.create(
                working_copy=MainContent.add_root(self.widgy_site).node,
            ),
            title='titleabc',
            slug='slugabc',
        )


class AdminView(PageSetup):
    def as_view(self, **kwargs):
        kwargs.setdefault('has_permission', lambda req: True)
        kwargs.setdefault('model', WidgyPage)
        return self.view_cls.as_view(**kwargs)

    def test_permissions(self):
        with self.assertRaises(PermissionDenied):
            forbid_everything = lambda req: False
            req = self.factory.get('/')
            self.as_view(has_permission=forbid_everything)(req, str(self.page.pk))


class TestClonePage(AdminView, TestCase):
    view_cls = ClonePageView

    def test_get(self):
        view = self.as_view(model=WidgyPage)

        resp = view(self.factory.get('/'), str(self.page.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.page.title, resp.rendered_content)
        self.assertNotIn(self.page.slug, resp.rendered_content)

    def test_post(self):
        self.page.root_node.working_copy.content.add_child(
            self.widgy_site, Button, text='buttontext')

        view = self.as_view(model=WidgyPage)
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

        button = new_page.root_node.working_copy.content.get_children()[0]
        self.assertEqual(button.text, 'buttontext')


class TestUnpublish(AdminView, TestCase):
    view_cls = UnpublishView

    def test_unpublish(self):
        self.assertEqual(self.page.status, CONTENT_STATUS_PUBLISHED)

        view = self.as_view(model=WidgyPage)
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


class AdminButtonsTestBase(PageSetup, UserSetup):
    urls = 'widgy.contrib.widgy_mezzanine.tests.test_core'

    def setUp(self):
        super(AdminButtonsTestBase, self).setUp()
        self.model_admin = WidgyPageAdmin(WidgyPage, admin.site)

    def test_save_and_commit_without_changes(self):
        req = self.factory.post('/')
        req.user = self.superuser

        self.model_admin._save_and_commit(req, self.page)
        self.assertEqual(self.page.root_node.commits.count(), 1)
        # save and commit again should not commit again when there are no
        # changes to commit
        self.model_admin._save_and_commit(req, self.page)
        self.assertEqual(self.page.root_node.commits.count(), 1)


@skipUnless(PAGE_BUILDER_INSTALLED, 'page_builder is not installed')
@override_settings(WIDGY_MEZZANINE_SITE=widgy_site)
class TestAdminButtons(AdminButtonsTestBase, TestCase):
    def setUp(self):
        super(TestAdminButtons, self).setUp()
        self.client.login(username='superuser', password='password')

    def test_status_embryo(self):
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_add')
        response = self.client.get(url)
        self.assertIn('Save', response.rendered_content)

    def test_status_embryo_save(self):
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_add')
        response = self.client.get(url)
        data = {
            '_continue': '',
            'title': 'Title',
            'slug': 'test_status_embryo_save',
            'root_node': ContentType.objects.get_for_model(DefaultLayout).pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        page = WidgyPage.objects.get(slug='test_status_embryo_save')
        self.assertEqual(page.status, CONTENT_STATUS_DRAFT)

    def test_save_and_commit(self):
        self.page.status = CONTENT_STATUS_DRAFT
        self.page.save()
        req = self.factory.post('/')
        req.user = self.superuser
        self.model_admin._save_and_commit(req, self.page)
        self.assertEqual(self.page.status, CONTENT_STATUS_PUBLISHED)

    def test_save_and_commit_without_permission(self):
        self.model_admin = WidgyPageAdmin(WidgyPage, admin.site)
        req = self.factory.post('/')
        req.user = self.staffuser

        self.staffuser.user_permissions.filter(codename='add_versioncommit').delete()

        with mock.patch('django.contrib.messages.error') as error_mock:
            self.model_admin._save_and_commit(req, self.page)
        error_mock.assert_called_with(req, mock.ANY)
        self.assertEqual(self.page.root_node.commits.count(), 0)

    def test_status_draft(self):
        self.page.status = CONTENT_STATUS_DRAFT
        self.page.save()
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_change', args=(self.page.pk,))
        response = self.client.get(url)
        self.assertIn('Save as Draft', response.rendered_content)
        self.assertIn('Publish', response.rendered_content)

    def test_status_published(self):
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_change', args=(self.page.pk,))
        response = self.client.get(url)
        self.assertIn('Publish Changes', response.rendered_content)

    def test_delete_button(self):
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_add')
        response = self.client.get(url)
        self.assertNotIn('Delete', response.rendered_content)
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_change', args=(self.page.pk,))
        response = self.client.get(url)
        self.assertIn('Delete', response.rendered_content)


@make_reviewed
class TestAdminButtonsWhenReviewed(AdminButtonsTestBase, TestCase):
    def test_save_and_commit(self):
        self.page.status = CONTENT_STATUS_DRAFT
        self.page.save()
        req = self.factory.post('/')
        req.user = self.staffuser
        self.model_admin._save_and_commit(req, self.page)
        self.assertEqual(self.page.status, CONTENT_STATUS_DRAFT)
        self.assertEqual(self.page.root_node.commits.count(), 1)
        commit = self.page.root_node.commits.get()
        self.assertFalse(commit.reviewedversioncommit.is_approved)

    def test_save_and_approve(self):
        self.page.status = CONTENT_STATUS_DRAFT
        self.page.save()
        req = self.factory.post('/')
        req.user = self.superuser
        self.model_admin._save_and_approve(req, self.page)
        self.assertEqual(self.page.status, CONTENT_STATUS_PUBLISHED)
        self.assertEqual(self.page.root_node.commits.count(), 1)
        self.assertTrue(self.page.root_node.head.reviewedversioncommit.is_approved)

    def test_save_and_approve_without_permission(self):
        req = self.factory.post('/')
        req.user = self.staffuser
        with mock.patch('django.contrib.messages.error') as error_mock:
            self.model_admin._save_and_approve(req, self.page)
        error_mock.assert_called_with(req, mock.ANY)
        self.assertEqual(self.page.root_node.commits.count(), 0)

    def test_save_and_approve_without_commit(self):
        commit = self.page.root_node.commit()
        req = self.factory.post('/')
        req.user = self.superuser
        self.model_admin._save_and_approve(req, self.page)
        self.assertTrue(refetch(commit).reviewedversioncommit.is_approved)
        self.assertEqual(self.page.root_node.commits.count(), 1)

    def test_save_and_commit_without_changes(self):
        with mock.patch('django.contrib.messages.warning') as warning_mock:
            super(TestAdminButtonsWhenReviewed, self).test_save_and_commit_without_changes()
        warning_mock.assert_called_with(mock.ANY, mock.ANY)

    def test_status_embryo(self):
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_add')
        # same for staff or superuser
        with self.as_user('staffuser'):
            response = self.client.get(url)
            self.assertIn('Save', response.rendered_content)

    def test_status_draft(self):
        self.page.status = CONTENT_STATUS_DRAFT
        self.page.save()
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_change', args=(self.page.pk,))
        with self.as_user('staffuser'):
            response = self.client.get(url)
            self.assertIn('Save as Draft', response.rendered_content)
            self.assertIn('Submit for Review', response.rendered_content)
            self.assertNotIn('_save_and_approve', response.rendered_content)
        with self.as_user('superuser'):
            response = self.client.get(url)
            self.assertIn('Save as Draft', response.rendered_content)
            self.assertIn('Submit for Review', response.rendered_content)
            self.assertIn('_save_and_approve', response.rendered_content)

    def test_status_published(self):
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_change', args=(self.page.pk,))
        with self.as_user('staffuser'):
            response = self.client.get(url)
            self.assertNotIn('Save as Draft', response.rendered_content)
            self.assertIn('Submit for Review', response.rendered_content)
            self.assertNotIn('_save_and_approve', response.rendered_content)
        with self.as_user('superuser'):
            response = self.client.get(url)
            self.assertNotIn('Save as Draft', response.rendered_content)
            self.assertIn('Submit for Review', response.rendered_content)


class TestAdminMessages(PageSetup, TestCase):
    urls = 'widgy.contrib.widgy_mezzanine.tests.test_core'

    def setUp(self):
        super(TestAdminMessages, self).setUp()
        self.user = User.objects.create_superuser('test', 'test@example.com', 'password')
        self.client.login(username='test', password='password')

    def test_future_schedule_message(self):
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_change', args=(self.page.pk,))
        self.page.root_node.commit(publish_at=timezone.now() + datetime.timedelta(days=1))
        response = self.client.get(url)
        self.assertIn('one future-scheduled commit', response.rendered_content)
        # make the future commit uninteresting
        self.page.root_node.commit()
        response = self.client.get(url)
        self.assertNotIn('future-scheduled commit', response.rendered_content)

    @make_reviewed
    def test_unapproved_commit_message(self):
        self.page = refetch(self.page)
        url = urlresolvers.reverse('admin:widgy_mezzanine_widgypage_change', args=(self.page.pk,))
        self.page.root_node.commit()
        response = self.client.get(url)
        self.assertIn('one unreviewed commit', response.rendered_content)
        # make the unreviewed commit uninteresting
        new_commit = self.page.root_node.commit()
        new_commit.approve(user=self.user)
        response = self.client.get(url)
        self.assertNotIn('unreviewed commit', response.rendered_content)


def refetch(obj):
    return obj.__class__.objects.get(pk=obj.pk)


@make_reviewed
class TestPublicationCommitHandling(PageSetup, TestCase):
    def setUp(self):
        super(TestPublicationCommitHandling, self).setUp()
        self.user = User.objects.create_superuser(
            username='asfd', password='asdfasdf', email='asdf@example.com',
        )

        self.vt = self.page.root_node

    def test_publish_on_commit(self):
        self.page.status = CONTENT_STATUS_DRAFT
        self.page.save()

        commit = self.vt.commit()
        commit.publish_at = timezone.now() + datetime.timedelta(days=1)

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_DRAFT)

        commit.approve(self.user)
        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)
        self.assertEqual(refetch(self.page).publish_date, refetch(commit).publish_at)

    def test_committing_again_does_nothing(self):
        self.page.status = CONTENT_STATUS_DRAFT
        self.page.save()

        commit = self.vt.commit()
        commit.approve(self.user)
        original_publish_date = refetch(self.page).publish_date

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)
        self.vt.commit(publish_at=timezone.now() + datetime.timedelta(days=1))

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)
        self.assertEqual(refetch(self.page).publish_date, original_publish_date)

    def test_publish_commit_moves_publish_date_up(self):
        self.page.publish_date = timezone.now() + datetime.timedelta(days=1)
        self.page.save()

        commit = self.vt.commit()
        commit.approve(self.user)
        self.assertEqual(refetch(self.page).publish_date, refetch(commit).publish_at)

    def test_unapprove_commit_unpublishes_page_when_there_are_no_other_published_commits(self):
        commit = self.vt.commit()
        commit.approve(self.user)
        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)

        commit.unapprove(self.user)

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_DRAFT)

    def test_unapprove_commit_corrects_publish_date_there_is_another_commit(self):
        c1 = self.vt.commit()
        c1.approve(self.user)

        c2 = self.vt.commit(publish_at=timezone.now() + datetime.timedelta(days=1))
        c2.approve(self.user)
        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)

        c1.unapprove(self.user)

        self.assertEqual(refetch(self.page).status, CONTENT_STATUS_PUBLISHED)
        self.assertEqual(refetch(self.page).publish_date, refetch(c2).publish_at)


class TestSelectRelated(PageSetup, TestCase):
    def test_default_manager_selects_related(self):
        p = Page.objects.get(pk=self.page.pk).widgypage
        with self.assertNumQueries(1):
            p.widgypage.root_node.head
