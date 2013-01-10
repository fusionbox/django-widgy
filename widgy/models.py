"""
Classes in this module supply the abstract models used to create new widgy
objects.
"""
from collections import defaultdict
from functools import partial

from django.db import models
from django.forms.models import modelform_factory, ModelForm
from django.forms import model_to_dict
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.contrib.admin import widgets

from treebeard.mp_tree import MP_Node

from widgy.exceptions import (
    InvalidTreeMovement,
    MutualRejection,
    BadChildRejection,
    BadParentRejection,
    ParentChildRejection,
    RootDisplacementError
)

from widgy.utils import exception_to_bool


class Node(MP_Node):
    """
    Instances of this class maintain the Materialized Path tree structure that
    the generic content is attached to.

    For more information, consult the Treebeard_ documentation.

    **Model Fields**:
        :content_type: ``models.ForeignKey(ContentType)``

        :content_id: ``models.PositiveIntegerField()``

        :content: ``generic.GenericForeignKey('content_type', 'content_id')``

    .. _Treebeard: https://tabo.pe/projects/django-treebeard/docs/1.61/index.html
    """
    content_type = models.ForeignKey(ContentType)
    content_id = models.PositiveIntegerField()
    content = generic.GenericForeignKey('content_type', 'content_id')

    def __unicode__(self):
        return str(self.content)

    def save(self, *args, **kwargs):
        created = not bool(self.pk)
        super(Node, self).save(*args, **kwargs)
        if created:
            self.content.post_create()

    def delete(self, *args, **kwargs):
        content = self.content
        super(Node, self).delete(*args, **kwargs)
        content.delete()

    def to_json(self, site):
        # reversed because we use 'right_id' and how backbone instantiates
        # nodes
        children = [c.to_json(site) for c in reversed(self.get_children())]
        json = {
            'url': self.get_api_url(site),
            'content': self.content.to_json(site),
            'children': children,
            'available_children_url': self.get_available_children_url(site),
        }
        parent = self.get_parent()
        if parent:
            json['parent_id'] = parent.get_api_url(site)

        right = self.get_next_sibling()
        json['right_id'] = right and right.get_api_url(site)

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

    def get_parent(self, *args, **kwargs):
        if hasattr(self, '_parent'):
            return self._parent
        return super(Node, self).get_parent(*args, **kwargs)

    def get_next_sibling(self):
        if hasattr(self, '_next_sibling'):
            return self._next_sibling
        return super(Node, self).get_next_sibling()

    def maybe_prefetch_tree(self):
        """
        Prefetch the tree unless it has already been prefetched
        """
        if not hasattr(self, '_children'):
            self.prefetch_tree()

    def prefetch_tree(self):
        """
        Builds the entire tree using python.  Each node has its Content
        instance filled in, and the reverse node relation on the content filled
        in as well.

        .. todo::

            Maybe use in_bulk here to avoid doing a query for every content
        """
        # Build a list with the current node and all descendants
        tree = [self] + list(self.get_descendants().order_by('path'))

        # This should get_depth() or is_root(), but both of those do another
        # query
        if self.depth == 1:
            self._parent = None
            self._next_sibling = None

        # Build a mapping of content_types -> ids
        contents = defaultdict(list)
        for node in tree:
            contents[node.content_type_id].append(node.content_id)

        # Convert that mapping to content_types -> Content instances
        content_types = ContentType.objects.in_bulk(contents.iterkeys())
        for content_type_id, content_ids in contents.iteritems():
            ct = content_types[content_type_id]
            contents[content_type_id] = dict([(i.id, i) for i in ct.model_class().objects.filter(pk__in=content_ids)])

        # Loop through the nodes both assigning the content instance and the
        # node instance onto the content
        for node in tree:
            node.content = contents[node.content_type_id][node.content_id]
            node.content.node = node

        # Knock the root node off before building out the tree structure
        tree.pop(0)
        self.consume_children(tree)
        assert not tree, "all of the nodes should be consumed"

    def consume_children(self, descendants):
        """
        Helper method to assign the proper children in the proper order to each
        node

        .. todo::
            fix the error messages
        """
        self._children = []

        while descendants:
            child = descendants[0]
            if child.depth == self.depth + 1 and child.path.startswith(self.path):
                if self._children:
                    self._children[-1]._next_sibling = child
                self._children.append(descendants.pop(0))
                child._next_sibling = None
                child._parent = self
                child.consume_children(descendants)
            else:
                break

    def get_api_url(self, site):
        return site.reverse(site.node_view, kwargs={'node_pk': self.pk})

    def get_available_children_url(self, site):
        return site.reverse(site.shelf_view, kwargs={'node_pk': self.pk})

    def reposition(self, right=None, parent=None):
        """
        Validates the requested node restructering and executes by calling :meth:`~Node.move` on
        the instance.

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
        return filter(
            exception_to_bool(self.content.validate_relationship, ParentChildRejection),
            classes)

    def filter_child_classes_recursive(self, classes):
        allowed_classes = {self: self.filter_child_classes(classes)}
        for child in self.get_children():
            allowed_classes.update(child.filter_child_classes_recursive(classes))
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
    # 0: can not pop out
    # 1: can pop out
    # 2: must pop out
    pop_out = 0

    form = ModelForm
    formfield_overrides = {}


    class Meta:
        abstract = True


    def __init__(self, *args, **kwargs):
        super(Content, self).__init__(*args, **kwargs)
        overrides = FORMFIELD_FOR_DBFIELD_DEFAULTS.copy()
        overrides.update(self.formfield_overrides)
        self.formfield_overrides = overrides

    def get_api_url(self, site):
        return site.reverse(site.content_view, kwargs={
            'object_name': self._meta.module_name,
            'app_label': self._meta.app_label,
            'object_pk': self.pk})

    def to_json(self, site):
        data = {
            'url': self.get_api_url(site),
            '__class__': self.class_name,
            'component': self.component_name,
            'model': self._meta.module_name,
            'object_name': self._meta.object_name,
            'draggable': self.draggable,
            'deletable': self.deletable,
            'accepting_children': self.accepting_children,
            'template_url': site.reverse(site.node_templates_view, kwargs={'node_pk': self.node.pk}),
            'preview_template': self.get_preview_template(),
            'pop_out': self.pop_out,
            'edit_url': site.reverse(site.node_edit_view, kwargs={'node_pk': self.node.pk}),
        }
        model_data = model_to_dict(self)
        del model_data[self._meta.pk.attname]
        data.update(model_data)
        return data

    @classmethod
    def class_to_json(cls, site):
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

    @property
    def class_name(self):
        """
        :Returns: a fully qualified classname including app_label and module_name
        """
        return "%s.%s" % (self._meta.app_label, self._meta.module_name)

    @property
    def component_name(self):
        """
        :Returns: a string that will be used clientside to retrieve this
        content's component.js resource.
        """
        return self.class_name

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

    @property
    def children(self):
        return [child.content for child in self.node.get_children()]

    def meta(self):
        return self._meta

    def get_form_class(self, request):
        """
        .. todo::
            memoize
        """
        defaults = {
            "form": self.form,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        return modelform_factory(self.__class__, **defaults)

    def valid_child_of(self, content):
        """
        Given a content instance, will we consent to be adopted by them?
        """
        return self.valid_child_class_of(content)

    @classmethod
    def valid_child_class_of(cls, content):
        """
        Given a `Content` instance, does our class consent to be adopted by them?
        """
        return True

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
            raise MutualRejection
        elif bad_parent:
            raise BadParentRejection
        elif bad_child:
            raise BadChildRejection

    @classmethod
    def add_root(cls, **kwargs):
        """
        Creates a new Content instance, stores it in the database, and calls
        ``Node.add_root``
        """
        obj = cls.objects.create(**kwargs)
        Node.add_root(content=obj)
        return obj

    def add_child(self, cls, **kwargs):
        obj = cls.objects.create(**kwargs)

        try:
            self.validate_relationship(obj)
        except ParentChildRejection:
            obj.delete()
            raise

        self.node.add_child(content=obj)
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

        self.node.add_sibling(content=obj, pos='left')
        return obj

    def get_children(self):
        return (i.content for i in self.node.get_children())

    def get_next_sibling(self):
        sib = self.node.get_next_sibling()
        return sib and sib.content

    def get_parent(self):
        parent = self.node.get_parent()
        return parent and parent.content

    def post_create(self):
        """
        Hook for custom code which needs to be run after creation.  Since the
        `Node` must be created after the content, any tree based actions
        have to happen after the save event has finished.
        """
        pass

    @property
    def preview_templates(self):
        """
        List of templates to search for the content template that is displayed
        in the editor to show a preview.

        -   ``widgy/{class_name}/preview.html``
        -   ``widgy/preview.html``
        """
        return (
            'widgy/%s/preview.html' % self.class_name,
            'widgy/preview.html',
        )

    @property
    def edit_templates(self):
        """
        List of templates to search for the edit form.

        -    ``widgy/{class_name}/edit_form.html``
        -    ``widgy/edit_form.html``
        """
        return (
            'widgy/%s/edit_form.html' % self.class_name,
            'widgy/edit_form.html',
        )

    def get_render_templates(self, context):
        """
        List of templates to search for the rendered template on the frontend.

        -    widgy/{module_name}.html
        -    widgy/{class_name}/{module_name}.html'
        """
        return (
            'widgy/%s.html' % self._meta.module_name,
            'widgy/%s/%s.html' % (self.class_name, self._meta.module_name),
        )

    def get_form_template(self, request, template=None, context=None):
        """
        :Returns: Rendered form template with the given context, if any.
        """
        if not context:
            context = RequestContext(request)
        context.update({'form': self.get_form_class(request)(instance=self)})
        return render_to_string(template or self.edit_templates, context)

    def get_preview_template(self, template=None, context={}):
        """
        :Returns: Rendered preview template with the given context, if any.
        """
        context.update({'self': self})
        return render_to_string(template or self.preview_templates, context)

    def render(self, context={}, template=None):
        """
        Renders the node in the given context.

        A ``template`` kwarg can be passed to use an explictly defined template
        instead of the default template list.
        """
        context.update({'content': self})
        rendered = render_to_string(
            template or self.get_render_templates(context),
            context
        )
        context.pop()
        return rendered

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance.

        If kwargs are given, they're passed to the form Field's constructor.
        """
        request = kwargs.pop("request", None)
        formfield = db_field.formfield(**kwargs)

        if isinstance(db_field, (models.ForeignKey, models.ManyToManyField)):
            from django.contrib.admin import site as admin_site
            related_modeladmin = admin_site._registry.get(db_field.rel.to)
            can_add_related = bool(related_modeladmin and related_modeladmin.has_add_permission(request))
            formfield.widget = widgets.RelatedFieldWidgetWrapper(
                formfield.widget, db_field.rel, admin_site,
                can_add_related=can_add_related)
        return formfield

    def get_templates(self, request):
        return {
            'edit_template': self.get_form_template(request),
        }
