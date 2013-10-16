Versioning
==========

Widgy comes with an optional but powerful versioning system inspired
by Git. Versioning works by putting another model called a version
tracker between the owner and the root node. Just like in Git, each
:class:`~widgy.models.VersionTracker` has a reference to a current
working copy and then a list of commits.  A
:class:`~widgy.models.VersionCommit` is a frozen snapshot of the
tree.

Versioning also supports delayed publishing of commits.  Normally
commits will be visible immediately, but it is possible to set a
publish time for a commit that allows a user to future publish content.

To enable versioning, all you need to do is use
:class:`widgy.db.fields.VersionedWidgyfield` instead of
:class:`widgy.db.fields.WidgyField`.


.. todo::

    diagram
