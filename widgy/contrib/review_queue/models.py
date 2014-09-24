from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from widgy.utils import QuerySet

from widgy.models.versioning import VersionTracker, VersionCommit


class ReviewedVersionCommit(VersionCommit):
    approved_by = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
                                    null=True, on_delete=models.PROTECT, related_name='+')
    approved_at = models.DateTimeField(default=None, null=True)

    class Meta:
        verbose_name = _('unapproved commit')
        verbose_name_plural = _('unapproved commits')


    class ReviewedVersionCommitQuerySet(QuerySet):
        def unapproved(self):
            return self.filter(approved_at__isnull=True,
                               approved_by__isnull=True)

        def approved(self):
            return self.exclude(approved_at__isnull=True,
                                approved_by__isnull=True)

    objects = ReviewedVersionCommitQuerySet.as_manager()

    @property
    def is_approved(self):
        return bool(self.approved_by_id and self.approved_at)

    def approve(self, user, commit=True):
        self.approved_at = timezone.now()
        self.approved_by = user
        if commit:
            self.save()

    def unapprove(self, user, commit=True):
        self.approved_at = None
        self.approved_by = None
        if commit:
            self.save()


class ReviewedVersionTracker(VersionTracker):
    commit_model = ReviewedVersionCommit

    class Meta:
        proxy = True

    class ReviewedVersionTrackerQuerySet(VersionTracker.VersionTrackerQuerySet):
        def published(self):
            return self.filter(
                commits__reviewedversioncommit__approved_by__isnull=False,
                commits__reviewedversioncommit__approved_at__isnull=False,
                # we must put this condition here instead of calling
                # super().published, because all of the conditions must be in
                # the same call to filter().
                commits__publish_at__lte=timezone.now(),
            ).distinct()

    objects = ReviewedVersionTrackerQuerySet.as_manager()

    def commit_is_ready(self, commit):
        return commit.is_published and commit.reviewedversioncommit.is_approved

    @property
    def commits(self):
        # XXX: This select_related is overriden in get_history_list.
        # This is useless now, but in the future, django will add the
        # ability to chain select_related as expected.
        # https://code.djangoproject.com/ticket/16855
        return super(ReviewedVersionTracker, self).commits \
            .select_related('reviewedversioncommit')

    def _commits_to_clone(self):
        for c in super(ReviewedVersionTracker, self)._commits_to_clone():
            yield c.reviewedversioncommit
