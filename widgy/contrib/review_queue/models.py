from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from fusionbox.db.models import QuerySetManager

from widgy.models.versioning import VersionTracker, VersionCommit


class ReviewedVersionCommit(VersionCommit):
    approved_by = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
                                    null=True, on_delete=models.PROTECT, related_name='+')
    approved_at = models.DateTimeField(default=None, null=True)

    class Meta:
        verbose_name = _('unapproved commit')
        verbose_name_plural = _('unapproved commits')

    objects = QuerySetManager()

    class QuerySet(QuerySet):
        def get_non_approved(self):
            return self.filter(approved_at__isnull=True,
                               approved_by__isnull=True)

    @property
    def is_approved(self):
        return bool(self.approved_by and self.approved_at)

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

    def get_published_node(self, request):
        for commit in self.get_history():
            if commit.is_published and commit.reviewedversioncommit.is_approved:
                return commit.root_node
        return None

    @property
    def commits(self):
        # XXX: This select_related is overriden in get_history_list.
        # This is useless now, but in the future, django will add the
        # ability to chain select_related as expected.
        # https://code.djangoproject.com/ticket/16855
        return super(ReviewedVersionTracker, self).commits \
            .select_related('reviewedversioncommit')
