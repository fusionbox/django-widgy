"""
Classes in this module supply the abstract models used to create new widgy
objects.
"""
from collections import defaultdict
from operator import attrgetter

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string

from treebeard.mp_tree import MP_Node

from widgy.exceptions import (InvalidTreeMovement, OhHellNo, BadChildRejection,
        BadParentRejection, ParentChildRejection, RootDisplacementError)

from widgy.utils import exception_to_bool


class Node(MP_Node):
    """
    Instances of this class maintain the Materialized Path tree structure that
    the generic content is attached to.

    .. Treebeard_

    **Model Fields**:
        :content_type: ``models.ForeignKey(ContentType)``

        :content_id: ``models.PositiveIntegerField()``

        :content: ``generic.GenericForeignKey('content_type', 'content_id')``
    """
    content_type = models.ForeignKey(ContentType)
    content_id = models.PositiveIntegerField()
    content = generic.GenericForeignKey('content_type', 'content_id')

    def save(self, *args, **kwargs):
        created = not bool(self.pk)
        super(Node, self).save(*args, **kwargs)
        if created:
            self.content.post_create()

    def delete(self, *args, **kwargs):
        content = self.content
        super(Node, self).delete(*args, **kwargs)
        content.delete()

    def to_json(self):
        # reversed because we use 'right_id' and how backbone instantiates
        # nodes
        children = [c.to_json() for c in self.get_children().reverse()]
        json = {
                'url': self.get_api_url(),
                'content': self.content.to_json(),
                'children': children,
                'available_children_url': self.get_available_children_url(),
                }
        parent = self.get_parent()
        if parent:
            json['parent_id'] = parent.get_api_url()

        right = self.get_next_sibling()
        json['right_id'] = right and right.get_api_url()

        return json

    def render(self, *args, **kwargs):
        """
        Delegates the render call to the content instance.
        """
        return self.content.render(*args, **kwargs)

    def get_children(self):
        """
        Wraps the MP_Tree API call to return the pre_built tree of children if
        it is present.
        """
        if hasattr(self, '_children'):
            return self._children
        return super(Node, self).get_children()

    def prefetch_tree(self):
        """
        Builds the entire tree using python.  Each node has its Content
        instance filled in, and the reverse node relation on the content filled
        in as well.

        .. todo::

            Maybe use in_bulk here to avoid doing a query for every content
        """
        # Build a list with the current node and all descendants
        tree = list(self.get_descendants()) + [self]

        # Build a mapping of content_types -> ids
        contents = defaultdict(list)
        for node in tree:
            contents[node.content_type_id].append(node.content_id)

        # Convert that mapping to content_types -> Content instances
        # TODO: Maybe use in_bulk here to avoid doing a query for every content
        # type
        for content_type_id, content_ids in contents.iteritems():
            ct = ContentType.objects.get(pk=content_type_id)
            contents[content_type_id] = dict([(i.id, i) for i in ct.model_class().objects.filter(pk__in=content_ids)])

        # Loop through the nodes both assigning the content instance and the
        # node instance onto the content
        for node in tree:
            node.content = contents[node.content_type_id][node.content_id]
            node.content.node = node

        # Knock the root node off before building out the tree structure
        tree.pop()

        self.assign_children(tree, True)

    def assign_children(self, descendants, sort=False):
        """
        Helper method to assign the proper children in the proper order to each
        node

        .. todo::
            fix the error messages
        """
        if sort:
            descendants.sort(key=attrgetter('depth', 'path'), reverse=True)

        self._children = []

        while descendants:
            child = descendants[-1]
            if child.depth == self.depth + 1 and child.path.startswith(self.path):
                self._children.append(descendants.pop())
            else:
                break

        for child in self._children:
            child.assign_children(descendants)

    @models.permalink
    def get_api_url(self):
        return ('widgy.views.node', (), {'node_pk': self.pk})

    @models.permalink
    def get_available_children_url(self):
        return ('widgy.views.recursive_children', (), {'node_pk': self.pk})

    def reposition(self, right=None, parent=None):
        """
        .. todo::
            fix the error messages
        """
        if not self.content.draggable:
            raise InvalidTreeMovement({'message': "You can't move me"})

        if right:
            if right.is_root():
                raise InvalidTreeMovement({'message': 'You can\'t move the root'})

            right.get_parent().content.validate_relationship(self.content)
            self.move(right, pos='left')
        elif parent:
            parent.content.validate_relationship(self.content)
            self.move(parent, pos='last-child')
        else:
            assert right or parent

    def filter_child_classes(self, classes):
        return set([c for c in classes if exception_to_bool(self.content.validate_relationship)(c)])

    def filter_child_classes_recursive(self, classes):
        allowed_classes = self.filter_child_classes(classes)
        for child in self.get_children():
            allowed_classes.update(child.filter_child_classes(classes))
        return allowed_classes


class Content(models.Model):
    """
    Abstract base class for all models that are intended to a part of a Widgy
    tree structure.

    **Model Fields**:
        :_nodes: ``generic.GenericRelation(Node,
                                   content_type_field='content_type',
                                   object_id_field='content_id')``
    """
    _nodes = generic.GenericRelation(Node,
                               content_type_field='content_type',
                               object_id_field='content_id')

    draggable = True            #: Set this content to be draggable
    deletable = True            #: Set this content instance to be deleteable
    accepting_children = False  #: Sets this content instance to be able to have children.

    class Meta:
        abstract = True

    @classmethod
    def valid_child_class_of(cls, content):
        """
        Given a content instance, does our class consent to be adopted by them?
        """
        return True

    @classmethod
    def class_to_json(cls):
        """
        :Returns: a json-able python object that represents the class type.
        """
        return {
                '__class__': "%s.%s" % (cls._meta.app_label, cls._meta.module_name),
                'title': cls._meta.verbose_name.title(),
                }

    @classmethod
    def all_concrete_subclasses(cls):
        """
        Recursively gathers all the non-abstract subclasses.
        """
        classes = set(c for c in cls.__subclasses__() if not c._meta.abstract)
        for c in cls.__subclasses__():
            classes.update(c.all_concrete_subclasses())
        return classes

    @classmethod
    def add_root(cls, **kwargs):
        """
        Creates a new Content instance, stores it in the database, and calls
        :method:`Node.add_root`
        """
        obj = cls.objects.create(**kwargs)
        Node.add_root(content=obj)
        return obj

    @property
    def node(self):
        """
        Settable property used by Node.prefetch_tree to optimize tree
        rendering
        """
        if hasattr(self, '_node'):
            return self._node
        return self._nodes.all()[0]

    @node.setter
    def node(self, value):
        self._node = value

    def valid_child_of(self, content):
        """
        Given a content instance, will we consent to be adopted by them?
        """
        return self.valid_child_class_of(content)

    def valid_parent_of_class(self, cls):
        """
        Given a content class, can it be _added_ as our child?
        Note: this does not apply to _existing_ children (adoption)
        """
        return self.accepting_children

    def valid_parent_of_instance(self, content):
        """
        Given a content instance, can we adopt them?
        """
        return self.valid_parent_of_class(type(content))

    def validate_relationship(self, child):
        parent = self
        if isinstance(child, Content):
            bad_parent = not child.valid_child_of(parent)
            bad_child = not parent.valid_parent_of_instance(child)
        else:
            bad_parent = not child.valid_child_class_of(parent)
            bad_child = not parent.valid_parent_of_class(child)

        if bad_parent and bad_child:
            raise OhHellNo
        elif bad_parent:
            raise BadParentRejection
        elif bad_child:
            raise BadChildRejection

    def add_child(self, cls, **kwargs):
        obj = cls.objects.create(**kwargs)

        try:
            self.validate_relationship(obj)
        except ParentChildRejection:
            obj.delete()
            raise

        self.node.add_child(
                content=obj
                )
        return obj

    def add_sibling(self, cls, **kwargs):
        if self.node.is_root():
            raise RootDisplacementError({'message': 'You can\'t put things next to me'})

        obj = cls.objects.create(**kwargs)
        parent = self.node.get_parent().content

        try:
            parent.validate_relationship(obj)
        except ParentChildRejection:
            obj.delete()
            raise

        self.node.add_sibling(
                content=obj,
                pos='left'
                )
        return obj

    def post_create(self):
        """
        Hook for custom code which needs to be run after creation.  Since the
        `Node` must be created after the widget, any tree based actions
        have to happen after the save event has finished.
        """
        pass

    @property
    def class_name(self):
        """
        :Returns: a fully qualified classname including app_label and module_name
        """
        return "%s.%s" % (self._meta.app_label, self._meta.module_name)

    @property
    def component_name(self):
        """
        :Returns: a string that will be used clientside to retrieve this content's component.js resource.
        """
        return self.class_name

    def to_json(self):
        return {
                'url': self.get_api_url(),
                '__class__': self.class_name,
                'component': self.component_name,
                'model': self._meta.module_name,
                'object_name': self._meta.object_name,
                'draggable': self.draggable,
                'deletable': self.deletable,
                'accepting_children': self.accepting_children,
                }

    @models.permalink
    def get_api_url(self):
        return ('widgy.views.content', (), {
            'object_name': self._meta.module_name,
            'app_label': self._meta.app_label,
            'object_pk': self.pk})

    def get_templates(self):
        templates = (
                'widgy/{module_name}.html'.format(module_name=self._meta.module_name),
                )
        return templates

    def render(self, context):
        context.update({'content': self})
        rendered_content = render_to_string(self.get_templates(), context)
        context.pop()
        return rendered_content
