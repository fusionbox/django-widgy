from __future__ import absolute_import
import datetime
import imp
import json

import django
from django.utils import timezone
from django.utils.functional import cached_property
from django.contrib.auth.models import Permission, User
from django.test.client import RequestFactory

from widgy.contrib.review_queue.site import ReviewedWidgySite
from widgy.contrib.review_queue.models import (
    ReviewedVersionTracker, ReviewedVersionCommit,
)

from .base import (
    RootNodeTestCase, refetch, SwitchUserTestCase,
)
from .test_api import TestApi
from ..models import ReviewedVersionedPage, RawTextWidget
from ..widgy_config import widgy_site


def make_tracker(site, vt_class=ReviewedVersionTracker):
    root_node = RawTextWidget.add_root(site, text='first').node
    tracker = vt_class.objects.create(working_copy=root_node)
    return tracker

def make_commit(site, delta=datetime.timedelta(0), vt_class=ReviewedVersionTracker):
    tracker = make_tracker(site, vt_class)
    commit = tracker.commit(publish_at=timezone.now() + delta)

    return (tracker, commit)


class TestApiReviewed(TestApi):
    widgy_site = ReviewedWidgySite()


class ReviewQueueTest(RootNodeTestCase):
    widgy_site = widgy_site

    def test_review_queue(self):
        tracker, commit1 = make_commit(self.widgy_site, vt_class=ReviewedVersionTracker)

        p = Permission.objects.get(codename='change_versioncommit')
        user = User.objects.create()
        user.user_permissions.add(p)
        user.save()

        request_factory = RequestFactory()

        tracker = refetch(tracker)
        self.assertFalse(tracker.get_published_node(request_factory.get('/')))

        commit1.approve(user)

        tracker = refetch(tracker)
        self.assertEqual(tracker.get_published_node(request_factory.get('/')),
                         commit1.root_node)

        commit2 = tracker.commit(publish_at=timezone.now())
        tracker = refetch(tracker)
        self.assertEqual(tracker.get_published_node(request_factory.get('/')),
                         commit1.root_node)

        commit2.approve(user)
        tracker = refetch(tracker)
        self.assertEqual(tracker.get_published_node(request_factory.get('/')),
                         commit2.root_node)

    def test_foreign_key_to_proxy_works(self):
        """
        If ReviewedVersionTracker is implemented as a proxy, ensure a
        foreign key returns a ReviewedVersionTracker instance (instead
        of the base model).
        """
        tracker, commit1 = make_commit(self.widgy_site, vt_class=ReviewedVersionTracker)
        page = ReviewedVersionedPage.objects.create(
            version_tracker=tracker,
        )

        page = ReviewedVersionedPage.objects.get(pk=page.pk)
        self.assertIsInstance(page.version_tracker, ReviewedVersionTracker)
        self.assertEqual(page.version_tracker, tracker)

    def test_clone_tracker(self):
        tracker, _ = make_commit(self.widgy_site, vt_class=ReviewedVersionTracker)

        new_tracker = tracker.clone()

        self.assertNotEqual(new_tracker.head.reviewedversioncommit.pk,
                            tracker.head.reviewedversioncommit.pk)


class ReviewQueueViewsTest(SwitchUserTestCase, RootNodeTestCase):
    widgy_site = ReviewedWidgySite()

    @cached_property
    def urls(self):
        urls = imp.new_module('urls')
        urls.urlpatterns = self.widgy_site.get_urls()
        return urls

    def test_commit_view(self):
        tracker, first_commit = make_commit(self.widgy_site)
        url = self.widgy_site.reverse(self.widgy_site.commit_view, kwargs={
            'pk': tracker.pk,
        })

        with self.as_staffuser() as user:
            with self.with_permission(user, 'add', ReviewedVersionCommit):
                self.client.post(url, {'approve_it': 1, 'publish_radio': 'now'})
                self.assertNotEqual(refetch(tracker).head.reviewedversioncommit, first_commit)
                self.assertFalse(refetch(tracker).head.reviewedversioncommit.is_approved)

        with self.as_staffuser() as user:
            with self.with_permission(user, 'change', ReviewedVersionCommit):
                with self.with_permission(user, 'add', ReviewedVersionCommit):
                    self.client.post(url, {'approve_it': 1, 'publish_radio': 'now'})
                    self.assertTrue(refetch(tracker).head.reviewedversioncommit.is_approved)

    def test_approve_view(self):
        tracker, commit = make_commit(self.widgy_site)
        url = self.widgy_site.reverse(self.widgy_site.approve_view, kwargs={
            'pk': tracker.pk,
            'commit_pk': commit.pk,
        })

        commit.message = u'\N{SNOWMAN}'
        commit.save()

        with self.as_staffuser() as user:
            resp = self.client.post(url)

        self.assertEqual(resp.status_code, 403)
        self.assertFalse(refetch(commit).is_approved)

        with self.as_staffuser() as user:
            with self.with_permission(user, 'change', ReviewedVersionCommit):
                resp = self.client.post(url)

        self.assertEqual(resp.status_code, 302)
        self.assertTrue(refetch(commit).is_approved)

    def test_unapprove_view(self):
        tracker, commit = make_commit(self.widgy_site)
        url = self.widgy_site.reverse(self.widgy_site.unapprove_view, kwargs={
            'pk': tracker.pk,
            'commit_pk': commit.pk,
        })
        commit.approve(self.user)

        with self.as_staffuser() as user:
            resp = self.client.post(url)

        self.assertEqual(resp.status_code, 403)
        self.assertTrue(refetch(commit).is_approved)

        with self.as_staffuser() as user:
            with self.with_permission(user, 'change', ReviewedVersionCommit):
                resp = self.client.post(url)

        self.assertEqual(resp.status_code, 302)
        self.assertFalse(refetch(commit).is_approved)

    def test_undo_approvals_view(self):
        tracker, commit = make_commit(self.widgy_site)
        tracker2, commit2 = make_commit(self.widgy_site)
        url = self.widgy_site.reverse(self.widgy_site.undo_approvals_view)
        commit.approve(self.user)
        commit2.approve(self.user)

        def doit():
            return self.client.post(url, {
                'actions': json.dumps([commit.pk]),
                'referer': '/referer/',
            })

        with self.as_staffuser() as user:
            resp = doit()

        self.assertEqual(resp.status_code, 403)
        self.assertTrue(refetch(commit).is_approved)
        self.assertTrue(refetch(commit2).is_approved)

        with self.as_staffuser() as user:
            with self.with_permission(user, 'change', ReviewedVersionCommit):
                resp = doit()

        self.assertEqual(resp.status_code, 302)
        if django.VERSION < (1, 9):
            self.assertEqual(resp['Location'], 'http://testserver/referer/')
        else:
            # https://docs.djangoproject.com/en/1.9/releases/1.9/#http-redirects-no-longer-forced-to-absolute-uris
            self.assertEqual(resp['Location'], '/referer/')
        self.assertFalse(refetch(commit).is_approved)
        self.assertTrue(refetch(commit2).is_approved)

    def test_undo_approvals_view_safe_redirect(self):
        tracker, commit = make_commit(self.widgy_site)
        url = self.widgy_site.reverse(self.widgy_site.undo_approvals_view)
        with self.as_staffuser() as user:
            with self.with_permission(user, 'change', ReviewedVersionCommit):
                for bad_url in ('http://example.com',
                                'https://example.com',
                                'ftp://exampel.com',
                                '//example.com'):

                    response = self.client.post(url, {
                        'actions': json.dumps([commit.pk]),
                        'referer': bad_url,
                    })
                    self.assertEqual(response.status_code, 302)
                    self.assertFalse(bad_url in response['Location'],
                                     "%s should be blocked" % bad_url)

                for good_url in ('/view/?param=http://example.com',
                                 '/view/?param=https://example.com',
                                 '/view?param=ftp://exampel.com',
                                 'view/?param=//example.com',
                                 '//testserver/',
                                 '/url%20with%20spaces/'):
                    response = self.client.post(url, {
                        'actions': json.dumps([commit.pk]),
                        'referer': good_url,
                    })
                    self.assertEqual(response.status_code, 302)
                    self.assertTrue(good_url in response['Location'],
                                    "%s should be allowed" % good_url)

    def test_published_versiontrackers(self):
        vt_class = self.widgy_site.get_version_tracker_model()
        tracker = make_tracker(self.widgy_site, vt_class)

        self.assertNotIn(tracker, vt_class.objects.published())

        commit = tracker.commit(publish_at=timezone.now())
        self.assertNotIn(tracker, vt_class.objects.published())
        commit.approve(self.user)
        self.assertIn(tracker, vt_class.objects.published())

        tracker2 = make_tracker(self.widgy_site, vt_class)
        self.assertIn(tracker, vt_class.objects.published())
        self.assertNotIn(tracker2, vt_class.objects.published())

        commit2 = tracker2.commit(publish_at=timezone.now())
        self.assertIn(tracker, vt_class.objects.published())
        self.assertNotIn(tracker2, vt_class.objects.published())

        other_commit = tracker.commit(publish_at=timezone.now())
        other_commit.approve(self.user)
        self.assertIn(tracker, vt_class.objects.published())
        self.assertNotIn(tracker2, vt_class.objects.published())

        commit2.approve(self.user)
        self.assertIn(tracker, vt_class.objects.published())
        self.assertIn(tracker2, vt_class.objects.published())

    def test_published_stickiness(self):
        vt_class = self.widgy_site.get_version_tracker_model()
        tracker = make_tracker(self.widgy_site, vt_class)

        # One commit is published, the other is approved. Since the same commit
        # is not both published and approved, the tracker is not published.

        c1 = tracker.commit(publish_at=timezone.now() + datetime.timedelta(days=1))
        c1.approve(self.user)

        tracker.commit(publish_at=timezone.now())
        self.assertNotIn(tracker, vt_class.objects.published())
