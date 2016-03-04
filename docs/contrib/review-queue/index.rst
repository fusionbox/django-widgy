Review Queue
============

.. currentmodule:: widgy.contrib.review_queue

Some companies have stricter policies for who can edit and who can publish
content on their websites. The review queue app is an extension to versioning
which collects commits for approval by a user with permissions.

The ``review_queue.change_reviewedversioncommit`` permission is used to
determine who is allowed to approve commits.

To enabled the review queue,

1.  Add ``widgy.contrib.review_queue`` to your
    :django:setting:`INSTALLED_APPS`.

2.  Your :class:`~widgy.site.WidgySite` needs to inherit from
    :class:`~site.ReviewedWidgySite`.

3.  Register a subclass of :class:`~admin.VersionCommitAdminBase`. ::

        from django.contrib import admin
        from widgy.contrib.review_queue.admin import VersionCommitAdminBase
        from widgy.contrib.review_queue.models import ReviewedVersionCommit

        class VersionCommitAdmin(VersionCommitAdminBase):
            def get_site(self):
                return my_site

        admin.site.register(ReviewedVersionCommit, VersionCommitAdmin)

    This step is unecessary if using ``widgy.contrib.widgy_mezzanine``.

4.  If upgrading from a non-reviewed site, a
    :class:`widgy.contrib.review_queue.models.ReviewedVersionCommit`
    object must be created for each :class:`widgy.models.VersionCommit`.
    There is a management command to do this for you. It assumes that
    all existing commits should be approved. ::

      ./manage.py populate_review_queue


.. class:: admin.VersionCommitAdminBase

    This an abstract :class:`~django:django.contrib.admin.ModelAdmin`
    class that displays the pending changes for approval. Any it abstract,
    because it doesn't know which :class:`~widgy.site.WidgySite` to use.

    .. method:: get_site(self)

        The :class:`~widgy.site.WidgySite` that this specific
        :class:`~admin.VersionCommitAdminBase` needs to work on.

.. note::

    The review queue's undo (it can undo approvals) support requires Django >=
    1.5 or the session-based ``MESSAGE_STORAGE``::

        MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
