from django.db import models
from widgy.db.fields import WidgyField

from widgy.utils import get_user_model

User = get_user_model()


class VersionTracker(models.Model):
    head = models.ForeignKey('VersionCommit', null=True)
    working_copy = models.ForeignKey('Node')

    class Meta:
        app_label = 'widgy'

    def commit(self, user=None):
        self.head = VersionCommit.objects.create(
            parent=self.head,
            author=user,
            root_node=self.working_copy.clone_tree(),
            tracker=self,
        )

        self.save()

        return self.head

    def revert_to(self, commit, user=None):
        self.head = VersionCommit.objects.create(
            parent=self.head,
            author=user,
            root_node=commit.root_node,
            tracker=self,
        )

        self.working_copy.delete()
        self.working_copy = commit.root_node.clone_tree(freeze=False)
        self.save()

        return self.head

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
            res.append(commit)
            commit_id = commit.parent_id
        return res


class VersionCommit(models.Model):
    tracker = models.ForeignKey(VersionTracker, related_name='commits')
    parent = models.ForeignKey('VersionCommit', null=True, on_delete=models.SET_NULL)
    root_node = WidgyField()
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'widgy'

    def __unicode__(self):
        return '%s %s' % (self.id, self.created_at)
