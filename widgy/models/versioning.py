from django.db import models
from django.db.models.query import QuerySet

from fusionbox.db.models import QuerySetManager

from widgy.utils import get_user_model
from widgy.db.fields import WidgyField
from widgy.models.base import Node

User = get_user_model()


class VersionTracker(models.Model):
    head = models.ForeignKey('VersionCommit', null=True, on_delete=models.PROTECT)
    working_copy = models.ForeignKey(Node, on_delete=models.PROTECT)

    class Meta:
        app_label = 'widgy'

    objects = QuerySetManager()

    class QuerySet(QuerySet):
        def orphan(self):
            """
            Filters the queryset to only include 'orphan' VersionTrackers. That
            is, VersionTrackers that have no objects pointing to them. This can
            be used to recover VersionTrackers whose parent object was deleted.
            """

            filters = {}
            for rel_obj in (self.model._meta.get_all_related_objects() +
                            self.model._meta.get_all_related_many_to_many_objects()):
                if not issubclass(rel_obj.model, VersionCommit):
                    name = rel_obj.field.rel.related_name or rel_obj.var_name
                    filters[name + '__isnull'] = True
            return self.filter(**filters)

    def commit(self, user=None, **kwargs):
        self.head = VersionCommit.objects.create(
            parent=self.head,
            author=user,
            root_node=self.working_copy.clone_tree(),
            tracker=self,
            **kwargs
        )

        self.save()

        return self.head

    def revert_to(self, commit, user=None, **kwargs):
        self.head = VersionCommit.objects.create(
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
        old_working_copy.delete()

    def get_published_node(self, request):
        return self.head.root_node

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


class VersionCommit(models.Model):
    tracker = models.ForeignKey(VersionTracker, related_name='commits')
    parent = models.ForeignKey('VersionCommit', null=True, on_delete=models.PROTECT)
    root_node = WidgyField(on_delete=models.PROTECT)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'widgy'

    def __unicode__(self):
        if self.message:
            subject = " - '%s'" % self.message.strip().split('\n')[0]
        else:
            subject = ''
        return '%s %s%s' % (self.id, self.created_at, subject)
