from __future__ import absolute_import
from pprint import pprint
import datetime
import time
import mock
import unittest
import contextlib

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.deletion import ProtectedError
from django.db import transaction

from widgy.models import Node, UnknownWidget, VersionTracker, Content, VersionCommit
from widgy.exceptions import (
    ParentWasRejected, ChildWasRejected, MutualRejection, InvalidTreeMovement,
    InvalidOperation, ParentChildRejection)
from widgy.views.versioning import daisydiff

from ..widgy_config import widgy_site
from ..models import (
    Layout, Bucket, RawTextWidget, CantGoAnywhereWidget, PickyBucket,
    ImmovableBucket, AnotherLayout, VowelBucket, VersionedPage, VersionedPage2,
    VersionedPage3, VersionedPage4, VersionPageThrough, Related,
    ForeignKeyWidget, WeirdPkBucket, UnnestableWidget, CssClassesWidget,
    CssClassesWidgetSubclass, CssClassesWidgetProperty, ManyToManyWidget, Tag
)
from .base import (
    RootNodeTestCase, make_a_nice_tree, SwitchUserTestCase, refetch)


class TestCore(RootNodeTestCase):
    widgy_site = widgy_site

    def test_post_create(self):
        """
        Content.post_create should be called after creating a content.
        """
        self.assertEqual(len(self.root_node.get_children()), 2)

    def test_deep(self):
        """
        A tree should be able to be at least 50 levels deep.
        """
        content = self.root_node.content
        for i in range(50):
            content = content.add_child(self.widgy_site,
                                        Bucket)

        # + 2 -- original buckets
        self.assertEqual(len(self.root_node.get_descendants()), 50 + 2)

    def test_validate_relationship_cls(self):
        try:
            self.widgy_site.validate_relationship(self.root_node.content, RawTextWidget)
        except ChildWasRejected as e:
            self.assertIn("Layout refuses to accept RawTextWidget.", str(e))
            self.assertTrue(e.message_dict)
        else:
            assert False, "Should have raised a ChildWasRejected exception"

        bucket = list(self.root_node.content.get_children())[0]
        try:
            self.widgy_site.validate_relationship(bucket, CantGoAnywhereWidget)
        except ParentWasRejected as e:
            self.assertIn("CantGoAnywhereWidget refuses to be put in Bucket.", str(e))
        else:
            assert False, "Should have raised a ParentWasRejected exception"

        try:
            self.widgy_site.validate_relationship(self.root_node.content, CantGoAnywhereWidget)
        except MutualRejection as e:
            self.assertIn("Neither Layout nor CantGoAnywhereWidget want to be together.", str(e))
        else:
            assert False, "Should have raised a MutualRejection exception"

    def test_validate_relationship_instance(self):
        picky_bucket = self.root_node.content.add_child(self.widgy_site,
                                                        PickyBucket)

        with self.assertRaises(ChildWasRejected):
            picky_bucket.add_child(self.widgy_site,
                                   RawTextWidget,
                                   text='aasdf')

        picky_bucket.add_child(self.widgy_site,
                               RawTextWidget,
                               text='hello')

        with self.assertRaises(ChildWasRejected):
            picky_bucket.add_child(self.widgy_site,
                                   Layout)

    def test_reposition_rechecks_deep_deep_compatibility(self):
        a = self.root_node.content.add_child(widgy_site, UnnestableWidget)
        first_bucket = self.root_node.content.add_child(widgy_site, Bucket)
        bucket = first_bucket.add_child(widgy_site, Bucket)
        b = bucket.add_child(widgy_site, UnnestableWidget)

        with self.assertRaises(ParentChildRejection):
            first_bucket.reposition(widgy_site, parent=a)

        self.assertEqual(len(a.get_children()), 0)
        self.assertEqual(bucket.get_parent(), first_bucket)

    def test_reposition_rechecks_deep_compatibility(self):
        a = self.root_node.content.add_child(widgy_site, UnnestableWidget)
        bucket = self.root_node.content.add_child(widgy_site, Bucket)
        b = bucket.add_child(widgy_site, UnnestableWidget)

        with self.assertRaises(ParentChildRejection):
            bucket.reposition(widgy_site, parent=a)

        self.assertEqual(len(a.get_children()), 0)
        self.assertEqual(bucket.get_parent(), self.root_node.content)

    def test_reposition_rechecks_deep_compatibility_old_right_node(self):
        # another test for all code paths of reposition's backout code
        a = self.root_node.content.add_child(widgy_site, UnnestableWidget)
        first_bucket = self.root_node.content.add_child(widgy_site, Bucket)
        bucket = first_bucket.add_sibling(widgy_site, Bucket)
        b = bucket.add_child(widgy_site, UnnestableWidget)

        with self.assertRaises(ParentChildRejection):
            bucket.reposition(widgy_site, parent=a)

        self.assertEqual(len(a.get_children()), 0)
        self.assertEqual(bucket.get_parent(), self.root_node.content)
        self.assertEqual(bucket.get_next_sibling(), first_bucket)

    def test_to_json_works_for_multi_table_inheritance(self):
        picky_bucket = self.root_node.content.add_child(self.widgy_site,
                                                        PickyBucket)
        picky_bucket.to_json(self.widgy_site)

    def test_css_classes_available_on_class(self):
        classes = self.root_node.content.to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('core_tests', 'layout'))
        classes = Layout.class_to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('core_tests', 'layout'))

    def test_css_classes_defined_as_class_attribute(self):
        css_classes_widget = CssClassesWidget.add_root(self.widgy_site)

        classes = css_classes_widget.to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('foo', 'bar'))
        classes = CssClassesWidget.class_to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('foo', 'bar'))

    def test_css_classes_defined_as_class_attribute_are_inherited(self):
        css_classes_widget = CssClassesWidgetSubclass.add_root(self.widgy_site)

        classes = css_classes_widget.to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('foo', 'bar'))
        classes = CssClassesWidgetSubclass.class_to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('foo', 'bar'))

    def test_css_classes_defined_as_property_method(self):
        css_classes_widget = CssClassesWidgetProperty.add_root(self.widgy_site)

        classes = css_classes_widget.to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('baz', 'qux'))

        # we don't test the class because property methods don't
        # work on classes.

    def test_css_classes_defined_on_the_instance(self):
        widget = self.root_node.content
        classes = widget.to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('core_tests', 'layout'))
        widget.css_classes = ('other',)
        classes = widget.to_json(self.widgy_site)['css_classes']
        self.assertEqual(classes, ('other',))

    def test_reposition(self):
        left, right = make_a_nice_tree(self.root_node)

        with self.assertRaises(InvalidTreeMovement):
            self.root_node.content.reposition(self.widgy_site, parent=left.content)

        with self.assertRaises(InvalidTreeMovement):
            left.content.reposition(self.widgy_site, right=self.root_node.content)

        # swap left and right
        right.content.reposition(self.widgy_site, right=left.content)

        new_left, new_right = self.root_node.get_children()
        self.assertEqual(right, new_left)
        self.assertEqual(left, new_right)

        raw_text = new_right.get_first_child()
        with self.assertRaises(ChildWasRejected):
            raw_text.content.reposition(self.widgy_site,
                                        parent=self.root_node.content,
                                        right=new_left.content)

        subbucket = list(new_right.get_children())[-1]
        subbucket.content.reposition(self.widgy_site,
                                     parent=self.root_node.content,
                                     right=new_left.content)
        new_subbucket, new_left, new_right = self.root_node.get_children()
        self.assertEqual(new_subbucket, subbucket)

    def test_proxy_model(self):
        bucket = VowelBucket.add_root(self.widgy_site)
        bucket = Node.objects.get(pk=bucket.node.pk).content
        bucket.add_child(self.widgy_site, ImmovableBucket)

        with self.assertRaises(ChildWasRejected):
            bucket.add_child(self.widgy_site, Bucket)

        bucket.add_child(self.widgy_site, ImmovableBucket)
        with self.assertRaises(ChildWasRejected):
            bucket.add_child(self.widgy_site, Bucket)

    def test_unkown_content_type(self):
        """
        A node with a ContentType whose model class can not be found should use
        an UnknownWidget in its place
        """
        fake_ct = ContentType.objects.create(
            name='fake',
            app_label='faaaaake',
        )
        self.root_node.content_type = fake_ct
        self.root_node.save()

        root_node = Node.objects.get(pk=self.root_node.pk)
        self.assertIsInstance(root_node.content, UnknownWidget)
        self.assertEqual(root_node.content.content_type.app_label, fake_ct.app_label)

    def test_unkown_content_type_prefetch(self):
        """
        prefetch_tree follows a different code path, so test it too
        """

        fake_ct = ContentType.objects.create(
            name='fake',
            app_label='faaaaake',
        )

        left, right = make_a_nice_tree(self.root_node)
        left.content_type = fake_ct
        left.save()

        root_node = Node.objects.get(pk=self.root_node.pk)
        root_node.prefetch_tree()
        content = list(root_node.content.get_children())[0].node.content
        self.assertIsInstance(content, UnknownWidget)
        self.assertEqual(content.content_type.app_label, fake_ct.app_label)

    def test_get_attributes(self):
        r = Related.objects.create()
        tests = [
            # (class, kwargs, attributes}
            (Bucket, {}, {}),
            (RawTextWidget, {'text': 'foo'}, {'text': 'foo'}),
            (AnotherLayout, {}, {}),
            (ForeignKeyWidget, {'foo': r}, {'foo_id': r.pk}),
        ]

        for cls, kwargs, attributes in tests:
            widget = cls.add_root(self.widgy_site, **kwargs)
            self.assertEqual(widget.get_attributes(),
                             attributes)

        widget = ManyToManyWidget.add_root(self.widgy_site)
        tag = Tag.objects.create(name='foo')
        widget.tags.add(tag)
        widget.save()
        self.assertEqual(widget.get_attributes(), {'tags': [tag.pk]})


class TestRegistry(RootNodeTestCase):
    def setUp(self):
        from widgy import Registry
        self.registry = Registry()

        class Test(Content):
            pass
        self.cls = Test

    def test_register(self):
        self.registry.register(self.cls)
        self.assertIn(self.cls, self.registry)

    def test_unregister(self):
        self.registry.register(self.cls)
        self.registry.unregister(self.cls)
        self.assertNotIn(self.cls, self.registry)

    def test_register_twice(self):
        self.registry.register(self.cls)
        with self.assertRaises(Exception):
            self.registry.register(self.cls)

    def test_unregister_not_registered(self):
        with self.assertRaises(Exception):
            self.registry.unregister(self.cls)


class TestTreesEqual(RootNodeTestCase):
    widgy_site = widgy_site

    def test_trees_equal_after_clone(self):
        left, right = make_a_nice_tree(self.root_node)
        new_root = self.root_node.clone_tree(freeze=False)
        self.assertTrue(self.root_node.trees_equal(new_root))
        new_root.content.get_children()[0].delete()
        self.assertFalse(self.root_node.trees_equal(new_root))

    def test_trees_unequal_content_type(self):
        a = CantGoAnywhereWidget.add_root(self.widgy_site)
        b = RawTextWidget.add_root(self.widgy_site, text='a')

        self.assertFalse(a.node.trees_equal(b.node))

    def test_trees_unequal_children(self):
        a = Bucket.add_root(self.widgy_site)
        a.add_child(self.widgy_site, RawTextWidget, text='a')
        a.add_child(self.widgy_site, RawTextWidget, text='b')

        b = Bucket.add_root(self.widgy_site)
        b.add_child(self.widgy_site, RawTextWidget, text='a')

        self.assertFalse(a.node.trees_equal(b.node))

    def test_trees_unequal_depth(self):
        a = Bucket.add_root(self.widgy_site).add_child(self.widgy_site, RawTextWidget, text='a')
        b = RawTextWidget.add_root(self.widgy_site, text='a')

        self.assertFalse(a.node.trees_equal(b.node))

    def test_trees_unequal_content(self):
        a = RawTextWidget.add_root(self.widgy_site, text='b')
        b = RawTextWidget.add_root(self.widgy_site, text='a')

        self.assertFalse(a.node.trees_equal(b.node))

    def test_trees_equal_equal(self):
        a = RawTextWidget.add_root(self.widgy_site, text='a')
        b = RawTextWidget.add_root(self.widgy_site, text='a')

        self.assertTrue(a.node.trees_equal(b.node))


def make_tracker(site, vt_class=VersionTracker):
    root_node = RawTextWidget.add_root(widgy_site, text='first').node
    tracker = vt_class.objects.create(working_copy=root_node)
    return tracker


def make_commit(site, delta=datetime.timedelta(0), vt_class=VersionTracker):
    tracker = make_tracker(site, vt_class)
    commit = tracker.commit(publish_at=timezone.now() + delta)

    return (tracker, commit)


class TestVersioning(RootNodeTestCase):
    widgy_site = widgy_site

    def test_clone_tree(self):
        left, right = make_a_nice_tree(self.root_node)

        new_tree = self.root_node.clone_tree()
        for a, b in zip(self.root_node.depth_first_order(),
                        new_tree.depth_first_order()):
            self.assertEqual(a.numchild, b.numchild)
            self.assertEqual(a.content_type_id, b.content_type_id)
            self.assertEqual(a.get_children_count(), b.get_children_count())
            self.assertEqual(b.content.get_attributes(), b.content.get_attributes())

    def test_clone_tree_doesnt_mutate_tree(self):
        make_a_nice_tree(self.root_node)
        self.root_node.prefetch_tree()
        before = self.root_node.depth_first_order()
        self.root_node.clone_tree()
        after = self.root_node.depth_first_order()
        self.assertEqual(before, after)

    def test_clone_tree_uses_prefetch(self):
        root = Bucket.add_root(self.widgy_site)
        root.add_child(self.widgy_site, RawTextWidget, text='a')
        root.add_child(self.widgy_site, RawTextWidget, text='b')

        root_node = root.node
        root_node.prefetch_tree()

        # - savepoint
        # - root content (1 query)
        # - release savepoint
        # - root node (2 queries, 2 savepoints)
        # - 2 text contents (2 queries, 2 savepoints)
        # - subnodes (1 query)
        with self.assertNumQueries(12):
            root_node.clone_tree()

    def test_content_equal(self):
        a = RawTextWidget.add_root(self.widgy_site, text='a')
        b = RawTextWidget.add_root(self.widgy_site, text='b')
        self.assertFalse(a.equal(b))
        b.text = 'a'
        b.save()
        self.assertTrue(a.equal(b))

    def test_content_equal_mti(self):
        a = AnotherLayout.add_root(self.widgy_site)
        b = AnotherLayout.add_root(self.widgy_site)
        self.assertTrue(a.equal(b))

    def test_commit(self):
        root_node = RawTextWidget.add_root(self.widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit1 = tracker.commit()

        self.assertNotEqual(tracker.working_copy, tracker.head.root_node)

        textwidget_content = tracker.working_copy.content
        textwidget_content.text = 'second'
        textwidget_content.save()
        commit2 = tracker.commit()

        self.assertEqual(commit1.root_node.content.text, 'first')
        self.assertEqual(commit2.root_node.content.text, 'second')

        self.assertEqual(commit2.parent, commit1)
        self.assertEqual(tracker.head, commit2)

    def test_tree_structure_versioned(self):
        root_node = Bucket.add_root(self.widgy_site).node
        root_node.content.add_child(
            self.widgy_site,
            RawTextWidget,
            text='a')
        root_node.content.add_child(
            self.widgy_site,
            RawTextWidget,
            text='b')

        # if the root_node isn't refetched, get_children is somehow empty. I
        # don't know why
        root_node = Node.objects.get(pk=root_node.pk)
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit1 = tracker.commit()

        new_a, new_b = tracker.working_copy.content.get_children()
        new_b.reposition(self.widgy_site, right=new_a)
        tracker.working_copy = Node.objects.get(pk=root_node.pk)
        commit2 = tracker.commit()
        self.assertEqual(['a', 'b'],
                         [i.content.text for i in commit1.root_node.get_children()])
        self.assertEqual(['b', 'a'],
                         [i.content.text for i in commit2.root_node.get_children()])

    def test_revert(self):
        root_node = RawTextWidget.add_root(self.widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit1 = tracker.commit()

        self.assertNotEqual(tracker.working_copy, tracker.head.root_node)

        textwidget_content = tracker.working_copy.content
        textwidget_content.text = 'second'
        textwidget_content.save()
        commit2 = tracker.commit()

        commit3 = tracker.revert_to(commit1)

        textwidget_content = tracker.working_copy.content
        textwidget_content.text = 'fourth'
        textwidget_content.save()

        commit4 = tracker.commit()

        self.assertEqual(['fourth', 'first', 'second', 'first'],
                         [i.root_node.content.text for i in tracker.get_history()])

    def test_get_history(self):
        root_node = RawTextWidget.add_root(self.widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)

        commits = reversed([tracker.commit() for i in range(6)])

        self.assertSequenceEqual(list(tracker.get_history()), list(commits))

    def test_old_contents_cant_change(self):
        root_node = RawTextWidget.add_root(self.widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit = tracker.commit()

        widget = commit.root_node.content
        widget.text = 'changed'
        with self.assertRaises(InvalidOperation):
            widget.save()

        self.assertEquals(Node.objects.get(pk=commit.root_node.pk).content.text, 'first')

        with self.assertRaises(InvalidOperation):
            widget.delete()

    def test_old_structure_cant_change(self):
        root_node = Bucket.add_root(self.widgy_site).node
        root_node.content.add_child(self.widgy_site, RawTextWidget, text='a')
        root_node.content.add_child(self.widgy_site, RawTextWidget, text='b')
        root_node = Node.objects.get(pk=root_node.pk)
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit = tracker.commit()

        a, b = Node.objects.get(pk=commit.root_node.pk).content.get_children()
        with self.assertRaises(InvalidOperation):
            b.reposition(self.widgy_site, right=a)

        with self.assertRaises(InvalidOperation):
            commit.root_node.content.add_child(self.widgy_site, RawTextWidget, text='c')

        self.assertEqual([i.content.text for i in commit.root_node.get_children()],
                         ['a', 'b'])

    def test_frozen_node(self):
        c = RawTextWidget.add_root(self.widgy_site)
        node = c.node
        node.is_frozen = True
        node.save()

        c.text = 'asdf'
        with self.assertRaises(InvalidOperation):
            c.save()

        with self.assertRaises(InvalidOperation):
            c.delete()

        self.assertEqual(RawTextWidget.objects.get(pk=c.pk).text, '')

        with self.assertRaises(InvalidOperation):
            node.delete()

    def test_frozen_node_raw(self):
        # even the treebeard methods called directly on the node should be frozen
        node = RawTextWidget.add_root(self.widgy_site).node
        node.is_frozen = True
        node.save()

        # 0 queries ensures that the exception is raised before any
        # modification takes place
        with self.assertNumQueries(0):
            with self.assertRaises(InvalidOperation):
                node.delete()

            with self.assertRaises(InvalidOperation):
                node.add_child()

            with self.assertRaises(InvalidOperation):
                node.add_child()

            with self.assertRaises(InvalidOperation):
                node.add_sibling()

            with self.assertRaises(InvalidOperation):
                node.move(node)

    def test_frozen_reposition(self):
        left, right = make_a_nice_tree(self.root_node)
        for node in self.root_node.depth_first_order():
            node.is_frozen = True
            node.save()

        left, right = Node.objects.get(pk=self.root_node.pk).get_children()

        before_ids = [i.id for i in self.root_node.depth_first_order()]

        with self.assertRaises(InvalidOperation):
            left.content.reposition(self.widgy_site, parent=right.content)

        with self.assertRaises(InvalidOperation):
            right.content.reposition(self.widgy_site, right=left.content)

        with self.assertRaises(InvalidOperation):
            right.content.add_child(self.widgy_site, RawTextWidget, text='asdf')

        with self.assertRaises(InvalidOperation):
            right.content.get_children()[0].add_sibling(self.widgy_site, RawTextWidget, text='asdf')

        root_node = Node.objects.get(pk=self.root_node.id)
        self.assertEqual([i.id for i in root_node.depth_first_order()],
                         before_ids)

    @unittest.expectedFailure
    def test_frozen_db_is_canonical(self):
        # I'm not sure if this failure should be expected or not. Should a node
        # always recheck the database value? Or, should we use a database
        # trigger to prevent modifications at the db level?
        root_node = RawTextWidget.add_root(self.widgy_site, text='asdf')

        a = Node.objects.get(pk=root_node.pk).content
        b = Node.objects.get(pk=root_node.pk).content
        # Node has to be set before we set is_frozen, otherwise the call to
        # delete will refetch the node.
        a.node
        b.node

        a.node.is_frozen = True
        a.save()

        # Even though the b _instance_ isn't frozen, the entry in the database
        # is. It would be ok if this was a database error instead of
        # InvalidOperation, like if a BEFORE UPDATE trigger prevented an
        # update.
        with self.assertRaises(InvalidOperation):
            b.delete()

    def test_prefetch_commits(self):
        root_node = RawTextWidget.add_root(self.widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)
        user = User.objects.create()
        commits = reversed([tracker.commit(user=user) for i in range(6)])

        with self.assertNumQueries(1):
            history = tracker.get_history_list()
            for commit in history:
                # root_node and author should be prefetched too
                commit.root_node.pk
                commit.author.pk

            self.assertEqual(list(commits), history)

        tracker = VersionTracker.objects.create(
            working_copy=RawTextWidget.add_root(self.widgy_site).node
        )
        self.assertEqual(tracker.get_history_list(), [])

    def orphan_helper(self):
        a = VersionedPage.objects.create()
        b = VersionedPage2.objects.create()
        c = VersionedPage4.objects.create()

        vt = VersionTracker.objects.create(working_copy=Layout.add_root(self.widgy_site).node)
        a.version_tracker = vt
        b.bar = vt
        a.save()
        b.save()

        VersionPageThrough.objects.create(
            widgy=vt,
            page=c,
        )

        return vt, a, b, c

    def test_orphan(self):
        vt, a, b, c = self.orphan_helper()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        a.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        b.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        c.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [vt])
        vt.delete()

        vt, a, b, c = self.orphan_helper()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        b.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        a.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        c.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [vt])

        vt.delete()

        vt, a, b, c = self.orphan_helper()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        a.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        c.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        b.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [vt])

        vt.delete()

        vt, a, b, c = self.orphan_helper()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        c.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        b.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        a.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [vt])

        vt.delete()

        vt, a, b, c = self.orphan_helper()
        vt.commit()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        c.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        b.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        a.delete()
        self.assertEqual(list(VersionTracker.objects.orphan()), [vt])

    def test_orphan_no_related_name(self):
        # VersionedPage3 doesn't have a related_name on its
        # VersionedWidgyField. Not having a related name is how you
        # opt-out of the orphan checking.
        vt, a, b, c = self.orphan_helper()
        self.assertEqual(list(VersionTracker.objects.orphan()), [])
        a.delete()
        b.delete()
        c.delete()

        self.assertEqual(list(VersionTracker.objects.orphan()), [vt])
        d = VersionedPage3.objects.create(foo=vt)
        self.assertEqual(list(VersionTracker.objects.orphan()), [vt])

    def test_deletion_prevented(self):
        """
        When widgets have outgoing foreign keys, cascade deletion shouldn't be
        able to affect a frozen widget.
        """

        related = Related.objects.create()
        root_node = ForeignKeyWidget.add_root(self.widgy_site, foo=related).node
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit = tracker.commit()

        # the related object must not be able to be deleted
        with self.assertRaises((ProtectedError, InvalidOperation)):
            commit.root_node.content.foo.delete()

        # the related object must still exist
        Related.objects.get(pk=related.pk)

        # the node and content must still exist
        Node.objects.get(pk=commit.root_node.pk)
        ForeignKeyWidget.objects.get(pk=commit.root_node.content.pk)

    def test_deep_deletion_prevented(self):
        # do the deletion on something other than the root node
        related = Related.objects.create()
        root_node = Bucket.add_root(self.widgy_site).node
        root_node.content.add_child(self.widgy_site, ForeignKeyWidget, foo=related)
        root_node = Node.objects.get(pk=root_node.pk)
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit = tracker.commit()

        # the related object must not be able to be deleted
        with self.assertRaises((ProtectedError, InvalidOperation)):
            with transaction.atomic():
                related.delete()

        # the related object must still exist
        Related.objects.get(pk=related.pk)

        # the node and content must still exist
        Node.objects.get(pk=commit.root_node.pk)
        ForeignKeyWidget.objects.get(pk=commit.root_node.content.get_children()[0].pk)

    def test_field_create(self):
        x = VersionedPage()
        x.version_tracker = ContentType.objects.get_for_model(Layout)
        x.save()
        self.assertIsInstance(x.version_tracker, VersionTracker)
        self.assertIsInstance(x.version_tracker.working_copy.content, Layout)

    def test_has_changes(self):
        left, right = make_a_nice_tree(self.root_node)
        vt = VersionTracker.objects.create(working_copy=self.root_node)
        self.assertTrue(vt.has_changes())
        vt.commit()
        self.assertFalse(vt.has_changes())
        left.content.add_child(self.widgy_site, RawTextWidget, text='foo')
        vt = VersionTracker.objects.get(pk=vt.pk)
        self.assertTrue(vt.has_changes())

    def test_daisydiff(self):
        a = """<html>
            <body>
                <p>foo
            </body>
        </html>"""

        b = """<html>
            <body>
                <p>bar
            </body>
        </html>"""

        diff = daisydiff(a, b)

        self.assertIn('foo', diff)
        self.assertIn('bar', diff)

    def test_daisydiff_unicode(self):
        a = u'\N{SNOWMAN}'
        b = u'\N{INTERROBANG}'

        diff = daisydiff(a, b)

        self.assertIn(a, diff)
        self.assertIn(b, diff)

    def test_reset(self):
        root_node = RawTextWidget.add_root(self.widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit1 = tracker.commit()

        textwidget_content = tracker.working_copy.content
        textwidget_content.text = 'second'
        textwidget_content.save()

        tracker.reset()
        # the content should get deleted
        self.assertFalse(RawTextWidget.objects.filter(pk=textwidget_content.pk).exists())
        textwidget_content = tracker.working_copy.content
        self.assertEqual(textwidget_content.text, 'first')

        # make sure working_copy is still editable
        textwidget_content = tracker.working_copy.content
        textwidget_content.text = 'second'
        textwidget_content.save()

        tracker.reset()
        textwidget_content = tracker.working_copy.content
        self.assertEqual(textwidget_content.text, 'first')

    def test_publish_at(self):
        tracker, commit1 = make_commit(self.widgy_site, datetime.timedelta(days=1))

        request_factory = RequestFactory()
        self.assertFalse(tracker.get_published_node(request_factory.get('/')))

    def test_multiple_publish_at(self):
        tracker, commit1 = make_commit(self.widgy_site, datetime.timedelta(days=-1))

        request_factory = RequestFactory()
        self.assertEqual(tracker.get_published_node(request_factory.get('/')),
                         commit1.root_node)

        commit2 = tracker.commit(publish_at=timezone.now() + datetime.timedelta(days=1))
        self.assertEqual(tracker.get_published_node(request_factory.get('/')),
                         commit1.root_node)

    def test_rollback_commit_publish(self):
        tracker, commit1 = make_commit(self.widgy_site, datetime.timedelta(days=1))

        request_factory = RequestFactory()

        commit2 = tracker.commit(publish_at=timezone.now() - datetime.timedelta(days=1))
        self.assertEqual(tracker.get_published_node(request_factory.get('/')),
                         commit2.root_node)

    def test_created_at(self):
        tracker, commit = make_commit(self.widgy_site)
        created_at = commit.created_at
        time.sleep(.1)
        commit.save()
        self.assertEqual(created_at, commit.created_at)

    def test_cloning_multi_table_inheritance(self):
        root = PickyBucket.add_root(self.widgy_site)
        new_root = root.clone()
        self.assertNotEqual(new_root.pk, root.pk)

    def test_cloning_multi_table_inheritance_fancy(self):
        root = WeirdPkBucket.add_root(self.widgy_site, bubble=2)
        new_root = root.clone()
        self.assertNotEqual(new_root.pk, root.pk)

    def test_clone_m2m(self):
        tag = Tag.objects.create(name='foo')
        root = ManyToManyWidget.add_root(self.widgy_site)
        root.tags.add(tag)

        new_root = root.clone()
        self.assertEqual(new_root.tags.get(), tag)

    def test_reset_exception(self):
        """
        Some widgets can't be deleted. We should still be able to reset.
        """

        tracker, commit1 = make_commit(self.widgy_site, datetime.timedelta(days=-1))

        with mock.patch.object(tracker.working_copy.content, 'delete') as delete:
            delete.side_effect = ProtectedError("can't delete", [])
            tracker.reset()
        # passes if there was no exception

    def test_delete(self):
        self.assertEqual(RawTextWidget.objects.count(), 0)
        tracker, commit = make_commit(self.widgy_site)
        self.assertNotEqual(RawTextWidget.objects.count(), 0)
        tracker.delete()
        self.assertEqual(RawTextWidget.objects.count(), 0)
        self.assertEqual(VersionTracker.objects.filter(pk=tracker.pk).count(), 0)

    def test_delete_deep_tree_and_multiple_commits(self):
        make_a_nice_tree(self.root_node)
        tracker = VersionTracker.objects.create(working_copy=self.root_node)
        tracker.commit()
        tracker.commit()
        tracker.delete()
        self.assertEqual(RawTextWidget.objects.count(), 0)
        self.assertEqual(VersionTracker.objects.filter(pk=tracker.pk).count(), 0)

    def test_delete_after_revert(self):
        tracker, commit = make_commit(self.widgy_site)
        tracker.commit()
        tracker.revert_to(commit)
        tracker.delete()

    def test_clone_tracker(self):
        tracker, _ = make_commit(self.widgy_site)
        tracker.commit()

        new_tracker = tracker.clone()

        self.assertNotEqual(tracker.pk, new_tracker.pk)
        self.assertNotEqual(tracker.working_copy, new_tracker.working_copy)
        self.assertEqual(len(tracker.get_history_list()),
                         len(new_tracker.get_history_list()))
        self.assertFalse(new_tracker.working_copy.is_frozen)

        for (commit, new_commit) in zip(tracker.commits.order_by('-id'), new_tracker.commits.order_by('-id')):
            self.assertNotEqual(commit.pk, new_commit.pk)
            self.assertEqual(new_commit.tracker, new_tracker)
        # the last commit
        self.assertEqual(new_commit.parent, None)


class VersioningViewsTest(SwitchUserTestCase, RootNodeTestCase):
    widgy_site = widgy_site

    def test_commit_view(self):
        tracker, first_commit = make_commit(self.widgy_site)

        url = self.widgy_site.reverse(self.widgy_site.commit_view, kwargs={
            'pk': tracker.pk,
        })

        with self.as_staffuser() as user:
            r = self.client.post(url, {'publish_radio': 'now'})
            self.assertEqual(r.status_code, 403)
            self.assertEquals(len(refetch(tracker).get_history_list()), 1)
            self.assertEqual(refetch(tracker).head, first_commit)

        with self.as_staffuser() as user:
            with self.with_permission(user, 'add', VersionCommit):
                r = self.client.post(url, {'publish_radio': 'now'})
                self.assertEqual(r.status_code, 200)
                self.assertEquals(len(refetch(tracker).get_history_list()), 2)

    def test_reset_view(self):
        tracker, commit = make_commit(self.widgy_site)

        url = self.widgy_site.reverse(self.widgy_site.reset_view, kwargs={
            'pk': tracker.pk,
        })


        root = tracker.working_copy.content
        root.text = 'changed'
        root.save()

        with self.as_staffuser() as user:
            r = self.client.post(url)
            self.assertEqual(r.status_code, 403)
            self.assertEqual(refetch(root).text, 'changed')

        with self.as_staffuser() as user:
            with self.with_permission(user, 'add', VersionCommit):
                r = self.client.post(url)
                self.assertEqual(r.status_code, 200)
                with self.assertRaises(RawTextWidget.DoesNotExist):
                    refetch(root)

    def test_revert_view(self):
        tracker, commit = make_commit(self.widgy_site)

        url = self.widgy_site.reverse(self.widgy_site.revert_view, kwargs={
            'pk': tracker.pk,
            'commit_pk': commit.pk,
        })


        with self.as_staffuser() as user:
            r = self.client.get(url)
            assert r.status_code == 200

            r = self.client.post(url, {'publish_radio': 'now'})
            self.assertEqual(r.status_code, 403)
            self.assertEquals(len(refetch(tracker).get_history_list()), 1)
            self.assertEqual(refetch(tracker).head, commit)

        with self.as_staffuser() as user:
            with self.with_permission(user, 'add', VersionCommit):
                r = self.client.post(url, {'publish_radio': 'now'})
                self.assertEqual(r.status_code, 200)
                self.assertEquals(len(refetch(tracker).get_history_list()), 2)


    def test_published_versiontrackers(self):
        vt_class = self.widgy_site.get_version_tracker_model()
        tracker = make_tracker(self.widgy_site, vt_class)

        self.assertNotIn(tracker, vt_class.objects.published())

        tracker.commit(publish_at=timezone.now())
        self.assertIn(tracker, vt_class.objects.published())

        tracker2 = make_tracker(self.widgy_site, vt_class)
        self.assertIn(tracker, vt_class.objects.published())
        self.assertNotIn(tracker2, vt_class.objects.published())

        tracker2.commit(publish_at=timezone.now())
        self.assertIn(tracker, vt_class.objects.published())
        self.assertIn(tracker2, vt_class.objects.published())


class TestPrefetchTree(RootNodeTestCase):
    widgy_site = widgy_site

    def setUp(self):
        super(TestPrefetchTree, self).setUp()
        make_a_nice_tree(self.root_node)
        # ensure the ContentType cache is filled
        for i in ContentType.objects.all():
            ContentType.objects.get_for_id(i.pk)

    def test_prefetch_tree(self):
        with self.assertNumQueries(1):
            root_node = Node.objects.get(pk=self.root_node.pk)

        # 4 queries:
        #  - get descendants of root_node
        #  - get bucket contents
        #  - get layout contents
        #  - get text contents
        with self.assertNumQueries(4):
            root_node.prefetch_tree()

        # maybe_prefetch_tree shouldn't prefetch the tree again
        with self.assertNumQueries(0):
            root_node.maybe_prefetch_tree()

        # we have the tree, verify its structure without executing any
        # queries
        with self.assertNumQueries(0):
            left, right = root_node.content.get_children()
            left_children = list(left.get_children())
            self.assertEqual(left_children[0].text, 'left_1')
            self.assertEqual(left_children[1].text, 'left_2')
            subbucket = left_children[2]
            subbucket_children = list(subbucket.get_children())
            self.assertEqual(subbucket_children[0].text, 'subbucket_1')
            self.assertEqual(subbucket_children[1].text, 'subbucket_2')

            right_children = list(right.get_children())
            self.assertEqual(right_children[0].text, 'right_1')
            self.assertEqual(right_children[1].text, 'right_2')
            self.assertTrue(all(isinstance(i, Content)
                                for i in root_node.content.depth_first_order()))

        # verify some convience methods are prefetched as well
        with self.assertNumQueries(0):
            # on the Content
            left, right = root_node.content.get_children()
            self.assertEqual(left.get_next_sibling(), right)
            self.assertEqual(right.get_next_sibling(), None)
            self.assertEqual(right.get_parent(), root_node.content)
            self.assertEqual(root_node.content.get_parent(), None)
            self.assertEqual(root_node.content.get_next_sibling(), None)
            self.assertEqual(left.get_ancestors(), [root_node.content])
            self.assertEqual(left.get_children()[0].get_ancestors(), [root_node.content, left])
            self.assertEqual(
                left.get_children()[2].get_children()[0].get_ancestors(),
                [root_node.content, left, left.get_children()[2]])

            self.assertEqual(left.get_root(), left.get_parent())
            self.assertEqual(left.get_children()[0].get_root(), left.get_parent())
            self.assertEqual(root_node.get_root(), root_node)

            # on the Node
            left, right = root_node.get_children()
            self.assertEqual(left.get_parent(), root_node)
            self.assertEqual(left.get_next_sibling(), right)
            self.assertEqual(right.get_next_sibling(), None)
            self.assertEqual(root_node.get_parent(), None)
            self.assertEqual(root_node.get_next_sibling(), None)
            # list() because get_ancestors() returns a querysetish thing
            self.assertEqual(list(root_node.get_ancestors()), [])
            self.assertEqual(list(left.get_ancestors()), [root_node])
            self.assertEqual(list(list(left.get_children())[0].get_ancestors()), [root_node, left])

            self.assertEqual(left.get_root(), left.get_parent())
            self.assertEqual(list(left.get_children())[0].get_root(), left.get_parent())

        # to_json shouldn't do any more queries either
        with self.assertNumQueries(0):
            root_node.to_json(self.widgy_site)

    def test_works_on_not_root_node(self):
        left_node = self.root_node.get_first_child()

        # 3 queries:
        #  - get descendants
        #  - get bucket contents
        #  - get text contents
        with self.assertNumQueries(3):
            left_node.prefetch_tree()

        with self.assertNumQueries(0):
            left = left_node.content
            left_children = list(left.get_children())
            self.assertEqual(left_children[0].text, 'left_1')
            self.assertEqual(left_children[1].text, 'left_2')
            subbucket = left_children[2]
            subbucket_children = list(subbucket.get_children())
            self.assertEqual(subbucket_children[0].text, 'subbucket_1')
            self.assertEqual(subbucket_children[1].text, 'subbucket_2')

        # For a non-root node, the parent and next sibling can't be computed by
        # prefetch_tree without another query for each one, so they may as well
        # be lazy
        right_node = list(self.root_node.get_children())[1]
        with self.assertNumQueries(2):
            self.assertEqual(left_node.get_parent(), self.root_node)
            self.assertEqual(left_node.get_next_sibling(), right_node)

        # get_ancestors must work correctly for non-root nodes, but it can't be
        # prefetched
        self.assertEqual(left.get_ancestors(), [left.get_parent()])
        self.assertEqual(left.get_children()[0].get_ancestors(), [left.get_parent(), left])

        self.assertEqual(left.get_root(), left.get_parent())
        self.assertEqual(left.get_children()[0].get_root(), left.get_parent())

    def test_prefetch_trees(self):
        a = Node.objects.get(pk=self.root_node.pk)
        b = Node.objects.get(pk=self.root_node.pk)

        # a.get_descendants, b.get_descendants
        # 3 contents
        with self.assertNumQueries(5):
            Node.prefetch_trees(a, b)

        root_node_dfo = self.root_node.depth_first_order()
        with self.assertNumQueries(0):
            a.content
            b.content
            self.assertEqual(root_node_dfo,
                             a.depth_first_order())
            self.assertEqual(a.depth_first_order(),
                             b.depth_first_order())

    def test_attach_content_instances(self):
        nodes = self.root_node.depth_first_order()
        nodes = Node.attach_content_instances(nodes)

        with self.assertNumQueries(0):
            for node in nodes:
                self.assertEqual(node.content.node, node)

    def test_content_node_is_set(self):
        # access .content
        self.root_node.content
        Node.attach_content_instances([self.root_node])
        with self.assertNumQueries(0):
            # node.content.node must get set even if node.content has already been accessed
            self.assertEqual(self.root_node.content.node, self.root_node)


class TestSite(TestCase):
    widgy_site = widgy_site

    def test_scss_location(self):
        scss_files = self.widgy_site.scss_files
        self.assertIn('widgy/core_tests/rawtextwidget.scss', scss_files)
        # widgy.Content will never have an scss file
        self.assertNotIn('widgy/models/content.scss', scss_files)

    def test_js_files(self):
        js_files = self.widgy_site.js_files
        self.assertIn('widgy/core_tests/rawtextwidget.js', js_files)
        self.assertNotIn('widgy/models/content.js', js_files)

    def test_admin_scss_files(self):
        files = self.widgy_site.admin_scss_files
        self.assertIn('widgy/core_tests/rawtextwidget.admin.scss', files)
        self.assertIn('widgy/core_tests/admin.scss', files)

        self.assertNotIn('widgy/models/content.scss', files)


class TestFindProblems(RootNodeTestCase):
    widgy_site = widgy_site

    def setUp(self):
        super(TestFindProblems, self).setUp()
        from django.db import connection
        self.cursor = connection.cursor()

    def test_dangling_content(self):
        left_bucket = self.root_node.content.get_children()[0]
        left_node = left_bucket.node
        self.cursor.execute('DELETE FROM core_tests_bucket WHERE id = %s', [str(left_bucket.id)])
        ids, _ = Node.find_widgy_problems()
        self.assertEqual(ids, [left_node.id])

    def test_unknown_widget(self):
        left_bucket = self.root_node.content.get_children()[0]
        fake_ct = ContentType.objects.create(
            name='fake',
            app_label='faaaaake',
        )
        left_node = left_bucket.node
        left_node.content_type_id = fake_ct.id
        left_node.save()

        _, ids = Node.find_widgy_problems()
        self.assertEqual(ids, [left_node.id])
