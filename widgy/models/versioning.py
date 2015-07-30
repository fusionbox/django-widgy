import copy

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.deletion import ProtectedError
from django.conf import settings
from django.template.defaultfilters import date as date_format

from widgy.db.fields import WidgyField
from widgy.models.base import Node
from widgy.utils import QuerySet, unset_pks


@python_2_unicode_compatible
class VersionCommit(models.Model):
    tracker = models.ForeignKey('VersionTracker', related_name='commits')
    parent = models.ForeignKey('VersionCommit', null=True, on_delete=models.PROTECT)
    root_node = WidgyField(on_delete=models.PROTECT)
    author = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
                               null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)
    publish_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'widgy'

    @property
    def is_published(self):
        return self.publish_at <= timezone.now()

    def __str__(self):
        if self.message:
            subject = " - '%s'" % self.message.strip().split('\n')[0]
        else:
            subject = ''
        date = date_format(self.created_at, 'DATETIME_FORMAT')
        return '#%s %s%s' % (self.id, date, subject)


class VersionTracker(models.Model):
    commit_model = VersionCommit

    head = models.ForeignKey('VersionCommit', null=True, on_delete=models.PROTECT, unique=True)
    working_copy = models.ForeignKey(Node, on_delete=models.PROTECT, unique=True)

    class Meta:
        app_label = 'widgy'

    class VersionTrackerQuerySet(QuerySet):
        def orphan(self):
            """
            Filters the queryset to only include 'orphan' VersionTrackers. That
            is, VersionTrackers that have no objects pointing to them. This can
            be used to recover VersionTrackers whose parent object was deleted.
            """

            filters = {}
            for rel_obj in (self.model._meta.get_all_related_objects() +
                            self.model._meta.get_all_related_many_to_many_objects()):
                if not issubclass(rel_obj.field.model, VersionCommit):
                    name = rel_obj.field.related_query_name()
                    filters[name + '__isnull'] = True
            return self.filter(**filters)

        def published(self):
            """
            Filter the queryset to only include version tracker that have a
            published commits.
            """
            return self.filter(commits__publish_at__lte=timezone.now()).distinct()

    objects = VersionTrackerQuerySet.as_manager()

    def commit(self, user=None, **kwargs):
        self.head = self.commit_model.objects.create(
            parent=self.head,
            author=user,
            root_node=self.working_copy.clone_tree(),
            tracker=self,
            **kwargs
        )

        self.save()

        return self.head

    def revert_to(self, commit, user=None, **kwargs):
        self.head = self.commit_model.objects.create(
            parent=self.head,
            author=user,
            root_node=commit.root_node,
            tracker=self,
            **kwargs
        )

        old_working_copy = self.working_copy
        self.working_copy = commit.root_node.clone_tree(freeze=False)
        # saving with the new working copy has to come before deleting the old
        # working copy, because foreign keys.
        self.save()
        old_working_copy.content.delete()

        return self.head

    def reset(self):
        old_working_copy = self.working_copy
        self.working_copy = self.head.root_node.clone_tree(freeze=False)
        self.save()
        try:
            old_working_copy.content.delete()
        except ProtectedError:
            # The tree couldn't be deleted, so just let it float away...
            pass

    def commit_is_ready(self, commit):
        """
        This method exists on the VersionTracker (instead of the VersionCommit)
        so that it is easier to override behavior in things like the
        review_queue.
        """
        return commit.is_published

    def get_published_node(self, request):
        for commit in self.get_history():
            if self.commit_is_ready(commit):
                return commit.root_node
        return None

    def get_history(self):
        """
        An iterator over commits, newest first.
        """

        commit = self.head
        while commit:
            yield commit
            commit = commit.parent

    def get_history_list(self):
        """
        A list of commits, newest first. Fetches them all in a single query.
        """

        commit_dict = dict((i.id, i) for i in self.commits.select_related('author', 'root_node'))
        res = []
        commit_id = self.head_id
        while commit_id:
            commit = commit_dict[commit_id]
            commit.tracker = self
            commit.parent = commit_dict.get(commit.parent_id)
            res.append(commit)
            commit_id = commit.parent_id
        return res

    def has_changes(self):
        if not self.head:
            return True
        else:
            newest_tree = self.head.root_node
            Node.prefetch_trees(self.working_copy, newest_tree)
            return not self.working_copy.trees_equal(newest_tree)

    def delete(self):
        commits = self.get_history_list()
        # break the circular reference
        self.head = None
        self.save()

        # Commits can share trees (it happens when reverting), so collect them
        # in a set in order to only delete them once.
        trees_to_delete = set([self.working_copy])
        for commit in commits:
            trees_to_delete.add(commit.root_node)
            commit.delete()

        super(VersionTracker, self).delete()

        for root_node in trees_to_delete:
            Node.get_tree(root_node).update(is_frozen=False)
            root_node.content.delete()

    @classmethod
    def get_owner_related_names(cls):
        """
        Names of reverse relationships of WidgyFields that point to us.
        """
        for rel_obj in cls._meta.get_all_related_objects():
            if isinstance(rel_obj.field, WidgyField):
                yield rel_obj.get_accessor_name()

    @cached_property
    def owners(self):
        return [owner
                for attr in self.get_owner_related_names()
                for owner in getattr(self, attr).all()]

    def clone(self):
        vt = copy.copy(self)
        vt.working_copy = vt.working_copy.clone_tree(freeze=False)
        commits = list(self._commits_to_clone())
        unset_pks(vt)
        vt.head = None
        vt.save()
        for commit in commits:
            commit.tracker = vt
            commit.parent = vt.head
            unset_pks(commit)
            commit.save()
            vt.head = commit
        vt.save()
        return vt

    def _commits_to_clone(self):
        return self.commits.order_by('id')
