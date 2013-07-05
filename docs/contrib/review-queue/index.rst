Review Queue
============

.. currentmodule:: widgy.contrib.review_queue

Some companies have stricter policies for who can edit and who can publish
content on their websites. The review queue app is an extension to versioning
which collects commits for approval by a user with permissions.

There are a couple of things that you need to do in order to enable the review
queue.

1.  Add ``widgy.contrib.review_queue`` to your
    :django:setting:`INSTALLED_APPS`.

2.  Your :class:`~widgy.site.WidgySite` needs to inherit from
    :class:`~site.ReviewedWidgySite`.

3.  For each model with a :class:`~widgy.db.fields.VersionedWidgyfield` that
    you want to add the review queue to, you will need to register a subclass
    of :class:`~admin.VersionCommitAdminBase` that implements the required
    methods.


.. class:: admin.VersionCommitAdminBase

    This an abstract :class:`~django:django.contrib.admin.options.ModelAdmin`
    class that displays the pending changes for approval. Any subclass of
    :class:`~admin.VersionCommitAdminBase` needs to implement three methods.

    .. method:: get_site(self)

        The :class:`~widgy.site.WidgySite` that this specific
        :class:`~admin.VersionCommitAdminBase` needs to work on.

    .. method:: get_commit_name(self, commit)

        A human-readable display name for that specific commit.

    .. method:: get_commit_preview_url(self, commit)

        A URL for previewing the commit.
