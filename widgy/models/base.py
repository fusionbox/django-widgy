"""
Classes in this module supply the abstract models used to create new widgy
objects.
"""
from collections import defaultdict
from functools import partial
import logging
import itertools
import copy

from django.db import models, transaction
from django import forms
from django.forms.models import modelform_factory, ModelForm
from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.admin import widgets
from django.template.defaultfilters import capfirst
from django.utils.encoding import force_text, python_2_unicode_compatible

from treebeard.mp_tree import MP_Node

from widgy.exceptions import (
    InvalidOperation,
    InvalidTreeMovement,
    ParentChildRejection,
    RootDisplacementError
)
from widgy.signals import pre_delete_widget
from widgy.generic import WidgyGenericForeignKey, ProxyGenericRelation
from widgy.utils import exception_to_bool, update_context, unset_pks
from widgy.widgets import DateTimeWidget, DateWidget, TimeWidget

logger = logging.getLogger(__name__)

# TODO: Don't use the Admin widgets.
FORMFIELD_FOR_DBFIELD_DEFAULTS = {
    models.DateTimeField: {
        'form_class': forms.SplitDateTimeField,
        'widget': DateTimeWidget
    },
    models.DateField: {'widget': DateWidget},
    models.TimeField: {'widget': TimeWidget},
}


@python_2_unicode_compatible
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
    content = WidgyGenericForeignKey('content_type', 'content_id')
    is_frozen = models.BooleanField(default=False)

    class Meta:
        app_label = 'widgy'
        unique_together = [('content_type', 'content_id')]

    def __str__(self):
        return force_text(self.content)

    def to_json(self, site):
        children = [c.to_json(site) for c in self.get_children()]
        json = {
            'url': self.get_api_url(site),
            'content': self.content.to_json(site),
            'children': children,
            'available_children_url': self.get_available_children_url(site),
            'possible_parents_url': self.get_possible_parents_url(site),
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
        if hasattr(self, '_children'):
            return self._children
        return super(Node, self).get_children()

    def get_parent(self, *args, **kwargs):
        if hasattr(self, '_parent'):
            return self._parent
        return super(Node, self).get_parent(*args, **kwargs)

    def get_next_sibling(self):
        if hasattr(self, '_parent'):
            if self._parent:
                siblings = list(self._parent.get_children())
            else:
                siblings = [self]
            try:
                return siblings[siblings.index(self) + 1]
            except IndexError:
                return None
        return super(Node, self).get_next_sibling()

    def get_ancestors(self):
        if hasattr(self, '_parent'):
            if self._parent:
                return list(self._parent.get_ancestors()) + [self._parent]
            else:
                return []
        return super(Node, self).get_ancestors()

    def get_root(self):
        if hasattr(self, '_parent'):
            if self._parent:
                return self._parent.get_root()
            else:
                return self
        return super(Node, self).get_root()

    def maybe_prefetch_tree(self):
        """
        Prefetch the tree unless it has already been prefetched
        """
        if not hasattr(self, '_children'):
            self.prefetch_tree()

    def depth_first_order(self):
        """
        All of the nodes in my tree (including myself) in depth-first order.
        """
        if hasattr(self, '_children'):
            ret = [self]
            for child in self.get_children():
                ret.extend(child.depth_first_order())
            return ret
        else:
            return [self] + list(self.get_descendants().order_by('path'))

    @staticmethod
    def fetch_content_instances(nodes):
        """
        Given a list of nodes, efficiently get all of their content instances.

        The structure returned looks like this::

            {
                content_type_id: {
                    content_id: content_instance,
                    content_id: content_instance,
                },
                content_type_id: {
                    content_id: content_instance,
                },
            }
        """
        # Build a mapping of content_types -> ids
        contents = defaultdict(set)
        for node in nodes:
            contents[node.content_type_id].add(node.content_id)

        # Convert that mapping to content_types -> Content instances
        for content_type_id, content_ids in contents.items():
            try:
                ct = ContentType.objects.get_for_id(content_type_id)
                model_class = ct.model_class()
            except AttributeError:
                # get_for_id raises AttributeError when there's no model_class in django < 1.6.
                model_class = None
            if model_class:
                contents[content_type_id] = ct.model_class().objects.in_bulk(content_ids)
            else:
                ct = ContentType.objects.get(id=content_type_id)
                contents[content_type_id] = dict((id, UnknownWidget(ct, id)) for id in content_ids)
                # Warn about using an UnknownWidget. It doesn't matter which instance we use.
                next(iter(contents[content_type_id].values()), UnknownWidget(ct, None)).warn()
        return contents

    @classmethod
    def attach_content_instances(cls, nodes):
        """
        Given a list of nodes, attach each one's Content. Efficiently.
        """
        needed_nodes = [i for i in nodes if '_content_cache' not in i.__dict__]
        contents = cls.fetch_content_instances(needed_nodes)
        for node in needed_nodes:
            node.content = contents[node.content_type_id][node.content_id]
        for node in nodes:
            node.content.node = node
        return nodes

    @classmethod
    def prefetch_trees(cls, *root_nodes):
        trees = [i.depth_first_order() for i in root_nodes]
        cls.attach_content_instances(list(itertools.chain(*trees)))
        for tree in trees:
            root_node = tree.pop(0)
            # This should get_depth() or is_root(), but both of those do
            # another query
            if root_node.depth == 1:
                root_node._parent = None
            root_node.consume_children(tree)
            assert not tree, "all of the nodes should be consumed"

    def prefetch_tree(self):
        """
        Builds the entire tree using python.  Each node has its Content
        instance filled in, and the reverse node relation on the content filled
        in as well.
        """
        self.prefetch_trees(self)

    def consume_children(self, descendants):
        """
        Helper method to assign the proper children in the proper order to each
        node
        """
        self._children = []

        while descendants:
            child = descendants[0]
            if child.depth == self.depth + 1:
                self._children.append(descendants.pop(0))
                child._parent = self
                child.consume_children(descendants)
            else:
                break

    def get_api_url(self, site):
        return site.reverse(site.node_view, kwargs={'node_pk': self.pk})

    def get_available_children_url(self, site):
        return site.reverse(site.shelf_view, kwargs={'node_pk': self.pk})

    def get_possible_parents_url(self, site):
        return site.reverse(site.node_parents_view, kwargs={'node_pk': self.pk})

    def filter_child_classes(self, site, classes):
        """
        What Content classes from `classes` would I let be my children?
        """

        validator = partial(site.validate_relationship, self.content)
        return list(filter(
            exception_to_bool(validator, ParentChildRejection),
            classes))

    def filter_child_classes_recursive(self, site, classes):
        """
        A dictionary of node objects to lists of content classes they would allow::

            {
                node_obj: [content_class, content_class, ...],
                 ...
            }
        """
        allowed_classes = {self: self.filter_child_classes(site, classes)}
        for child in self.get_children():
            allowed_classes.update(child.filter_child_classes_recursive(site, classes))
        return allowed_classes

    def possible_parents(self, site, root_node):
        """
        Where in root_node's tree can I be moved?
        """

        validator = exception_to_bool(
            partial(site.validate_relationship, child=self.content),
            ParentChildRejection)
        all_nodes = root_node.depth_first_order()
        my_family = set(self.depth_first_order())
        return [i for i in all_nodes if validator(i.content) and i not in my_family]

    @transaction.atomic(savepoint=False)
    def clone_tree(self, freeze=True):
        """
        1. new_root <- root_node
        2. new_root.content <- Clone(root_node.content)
        3. Insert new_root.
        4. children <- All descendents of root node.
        5. Iterate over children as child:
            i. unset PK
            ii. replace child.path[0:steplen] with new_root.path
            iii. cloned_content <- child.content
            iv. content_id <- cloned_content.pk
        6. Issue a bulk_create for children.
        """
        # This method only supports cloning an entire tree. We don't need it
        # for versioning, and I'm not sure what the semantics would be.
        cls = self.__class__
        assert self.depth == 1
        self.maybe_prefetch_tree()
        new_root = cls.add_root(
            content=self.content.clone(),
            numchild=self.numchild,
            is_frozen=freeze,
        )
        children_to_create = []
        for child in self.depth_first_order()[1:]:
            children_to_create.append(Node(
                content=child.content.clone(),
                path=new_root.path + child.path[cls.steplen:],
                is_frozen=freeze,
                depth=child.depth,
                numchild=child.numchild,
            ))
        cls.objects.bulk_create(children_to_create)
        return new_root

    def check_frozen(self):
        if self.is_frozen:
            raise InvalidOperation({'message': "This widget is uneditable."})

    @transaction.atomic(savepoint=False)
    def delete(self, *args, **kwargs):
        self.check_frozen()
        return super(Node, self).delete(*args, **kwargs)

    @transaction.atomic(savepoint=False)
    def add_child(self, *args, **kwargs):
        self.check_frozen()
        return super(Node, self).add_child(*args, **kwargs)

    @transaction.atomic(savepoint=False)
    def add_sibling(self, *args, **kwargs):
        self.check_frozen()
        return super(Node, self).add_sibling(*args, **kwargs)

    @transaction.atomic(savepoint=False)
    def move(self, *args, **kwargs):
        self.check_frozen()
        return super(Node, self).move(*args, **kwargs)

    def trees_equal(self, other):
        if self.content_type_id != other.content_type_id:
            return False
        if not self.get_depth() == other.get_depth():
            return False
        if not self.get_children_count() == other.get_children_count():
            return False
        if not self.content.equal(other.content):
            return False

        for child, other_child in zip(self.get_children(), other.get_children()):
            if not child.trees_equal(other_child):
                return False
        return True

    @classmethod
    def find_widgy_problems(cls, site=None):
        """
        Searches all the nodes for inconsistencies.

            - Nodes whose content doesn't exist
            - Nodes whose content types don't exist (UnknownWidgets)

        TODO: Maybe check for Content instances that don't have any nodes
        pointing to them.
        """

        dangling, unknown = [], []

        for node in cls.objects.all():
            content = node.content
            if not content:
                dangling.append(node.id)
            elif isinstance(content, UnknownWidget):
                unknown.append(node.id)

        return dangling, unknown


def check_frozen(sender, instance, **kwargs):
    instance.check_frozen()

models.signals.pre_delete.connect(check_frozen, sender=Node)


class Content(models.Model):
    """
    Abstract base class for all models that are intended to a part of a Widgy
    tree structure.

    **Model Fields**:
        :_nodes: ``generic.GenericRelation(Node,
                                   content_type_field='content_type',
                                   object_id_field='content_id')``
    """
    _nodes = ProxyGenericRelation(Node,
                                  content_type_field='content_type',
                                  object_id_field='content_id')


    # these preferences only affect the frontend interface and editing through
    # the API
    draggable = True
    deletable = True
    editable = False
    accepting_children = False
    shelf = False
    tooltip = None

    component_name = 'widget'

    CANNOT_POP_OUT = 0
    CAN_POP_OUT = 1
    MUST_POP_OUT = 2

    pop_out = CANNOT_POP_OUT

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
            'object_name': self._meta.model_name,
            'app_label': self._meta.app_label,
            'object_pk': self.pk})

    def to_json(self, site):
        node_pk_kwargs = {'node_pk': self.node.pk}
        data = {
            'url': self.get_api_url(site),
            '__class__': self.class_name,
            'css_classes': self.get_css_classes(),
            'component': self.component_name,
            'model': self._meta.model_name,
            'object_name': self._meta.object_name,
            'draggable': self.draggable,
            'deletable': self.deletable,
            'accepting_children': self.accepting_children,
            'template_url': site.reverse(site.node_templates_view, kwargs=node_pk_kwargs),
            'preview_template': self.get_preview_template(site),
            'pop_out': self.pop_out,
            'shelf': self.shelf,
            'attributes': self.get_attributes(),
            'form_prefix': self.get_form_prefix(),
            'display_name': self.display_name,
        }
        if self.editable:
            data['edit_url'] = site.reverse(site.node_edit_view, kwargs=node_pk_kwargs)
        return data

    def get_attributes(self):
        model_data = {}
        for field in self._meta.concrete_fields:
            if field.serialize:
                model_data[field.attname] = field.value_from_object(self)
        for field in self._meta.many_to_many:
            # this is copied from django.forms.models.model_to_dict
            if self.pk is None:
                model_data[field.name] = []
            else:
                qs = field.value_from_object(self)
                if qs._result_cache is not None:
                    model_data[field.name] = [item.pk for item in qs]
                else:
                    model_data[field.name] = list(qs.values_list('pk', flat=True))
        return model_data

    @classmethod
    def class_to_json(cls, site):
        """
        :Returns: a json-able python object that represents the class type.
        """
        return {
            '__class__': "%s.%s" % (cls._meta.app_label, cls._meta.model_name),
            'title': capfirst(cls._meta.verbose_name),
            'css_classes': cls.get_class_css_classes(),
            'tooltip': cls.tooltip and force_text(cls.tooltip),
        }

    @property
    def display_name(self):
        return force_text(self._meta.verbose_name)

    @property
    def class_name(self):
        """
        :Returns: a fully qualified classname including app_label and model_name
        """
        return "%s.%s" % (self._meta.app_label, self._meta.model_name)

    @classmethod
    def get_class_css_classes(cls):
        if hasattr(cls, 'css_classes'):
            return cls.css_classes
        return (cls._meta.app_label, cls._meta.model_name)

    def get_css_classes(self):
        if hasattr(self, 'css_classes'):
            return self.css_classes
        return self.get_class_css_classes()

    @property
    def node(self):
        """
        Settable property used by Node.prefetch_tree to optimize tree
        rendering
        """
        if hasattr(self, '_node'):
            return self._node
        try:
            return self._nodes.all()[0]
        except IndexError:
            raise Node.DoesNotExist

    @node.setter
    def node(self, value):
        self._node = value

    def get_root(self):
        return self.node.get_root().content

    def get_ancestors(self):
        ancestors = Node.attach_content_instances(self.node.get_ancestors())
        return [node.content for node in ancestors]

    def depth_first_order(self):
        nodes = Node.attach_content_instances(self.node.depth_first_order())
        return [node.content for node in nodes]

    def get_children(self):
        node_children = Node.attach_content_instances(self.node.get_children())
        return [node.content for node in node_children]

    def get_next_sibling(self):
        sib = self.node.get_next_sibling()
        return sib and sib.content

    def get_parent(self):
        parent = self.node.get_parent()
        return parent and parent.content

    def get_form_class(self, request):
        defaults = {
            "form": self.form,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            "fields": "__all__",
        }
        form_class = modelform_factory(self.__class__, **defaults)
        # Rather than make everybody subclass a special form, add the
        # required_css_class and error_css_class manually here, because we know
        # we need it in the widgy editor.  If need be, we can make the actual
        # classes configurable somehow later.
        if not hasattr(form_class, 'required_css_class'):
            form_class.required_css_class = 'required'
        if not hasattr(form_class, 'error_css_class'):
            form_class.error_css_class = 'error'
        return form_class

    def get_form_prefix(self):
        return self.node.pk

    def get_form(self, request, **form_kwargs):
        form_class = self.get_form_class(request)
        form_kwargs.setdefault('instance', self)
        return form_class(**form_kwargs)

    def valid_parent_of(self, cls, obj=None):
        """
        Given a content class, can it be _added_ as our child?
        Note: this does not apply to _existing_ children (adoption)
        """
        return self.accepting_children

    @classmethod
    def valid_child_of(cls, parent, obj=None):
        """
        Given a `Content` instance, does our class consent to be adopted by them?
        """
        return True

    @classmethod
    @transaction.atomic
    def add_root(cls, site, **kwargs):
        """
        Creates a new Content instance, stores it in the database, and calls
        ``Node.add_root``
        """
        obj = cls.objects.create(**kwargs)
        Node.add_root(content=obj)
        obj.post_create(site)
        return obj

    @transaction.atomic
    def add_child(self, site, cls, **kwargs):
        self.check_frozen()
        obj = cls.objects.create(**kwargs)
        self.node.add_child(content=obj)

        try:
            site.validate_relationship(self, obj)
        except:
            obj.delete(raw=True)
            raise

        obj.post_create(site)
        return obj

    @transaction.atomic
    def add_sibling(self, site, cls, **kwargs):
        self.check_frozen()
        if self.node.is_root():
            raise RootDisplacementError({'message': 'You can\'t put things next to me'})

        obj = cls.objects.create(**kwargs)
        self.node.add_sibling(content=obj, pos='left')
        parent = self.node.get_parent().content

        try:
            site.validate_relationship(parent, obj)
        except ParentChildRejection:
            obj.delete(raw=True)
            raise

        obj.post_create(site)
        return obj

    def post_create(self, site):
        """
        Hook for custom code which needs to be run after creation.  Since the
        `Node` must be created after the content, any tree based actions
        have to happen after the save event has finished.
        """
        pass

    @classmethod
    def get_templates_hierarchy(cls, **kwargs):
        templates = kwargs.get('hierarchy', (
            'widgy/{app_label}/{model_name}/{template_name}{extension}',
            'widgy/{app_label}/{template_name}{extension}',
            'widgy/{template_name}{extension}',
        ))
        kwargs.setdefault('extension', '.html')

        ret = []
        for template in templates:
            for parent_cls in cls.__mro__:
                try:
                    ret.extend(
                        template.format(**i) for i in parent_cls.get_template_kwargs(**kwargs)
                    )
                except AttributeError:
                    pass
        # This must return a list or tuple because
        # django.template.render_to_string does a typecheck.
        return ret

    @classmethod
    def get_template_kwargs(cls, **kwargs):
        defaults = {
            'app_label': cls._meta.app_label,
            'model_name': cls._meta.model_name,
        }
        defaults.update(**kwargs)

        return [defaults]

    @property
    def preview_templates(self):
        """
        List of templates to search for the content template that is displayed
        in the editor to show a preview.
        """
        return self.get_templates_hierarchy(template_name='preview')

    @property
    def edit_templates(self):
        """
        List of templates to search for the edit form.
        """
        return self.get_templates_hierarchy(template_name='edit')

    def get_render_templates(self, context):
        """
        List of templates to search for the rendered template on the frontend.
        """
        return self.get_templates_hierarchy(template_name='render')

    def get_form_template(self, request, template=None, context=None):
        """
        :Returns: Rendered form template with the given context, if any.
        """
        if not context:
            context = RequestContext(request)
        with update_context(context, {'form': self.get_form(request, prefix=self.get_form_prefix())}):
            return render_to_string(template or self.edit_templates, context)

    def get_preview_template(self, site):
        """
        :Returns: Rendered preview template.
        """
        return render_to_string(self.preview_templates, {
            'self': self,
            'edit_url': site.reverse(site.node_edit_view, kwargs={
                'node_pk': self.node.pk,
            }),
            'site': site,
        })

    def render(self, context, template=None):
        """
        A ``template`` kwarg can be passed to use an explictly defined template
        instead of the default template list.
        """
        with update_context(context, {'self': self}):
            return render_to_string(
                template or self.get_render_templates(context),
                context
            )

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Hook for specifying the form Field instance for a given database Field
        instance.

        If kwargs are given, they're passed to the form Field's constructor.
        """
        request = kwargs.pop("request")
        formfield = db_field.formfield(**kwargs)

        if formfield and isinstance(db_field, (models.ForeignKey, models.ManyToManyField)):
            from django.contrib.admin import site as admin_site
            related_modeladmin = admin_site._registry.get(db_field.rel.to)
            can_add_related = bool(related_modeladmin and
                                   related_modeladmin.has_add_permission(request))
            formfield.widget = widgets.RelatedFieldWidgetWrapper(
                formfield.widget, db_field.rel, admin_site,
                can_add_related=can_add_related)
        else:
            for klass in db_field.__class__.mro():
                if klass in self.formfield_overrides:
                    kwargs = dict(copy.deepcopy(self.formfield_overrides[klass]), **kwargs)
                    return db_field.formfield(**kwargs)
        return formfield

    def get_templates(self, request):
        return {
            'edit_template': self.get_form_template(request),
        }

    @transaction.atomic
    def reposition(self, site, right=None, parent=None):
        self.check_frozen()
        old_parent_node = self.node.get_parent()
        old_right_node = self.node.get_next_sibling()
        if right:
            if right.node.is_root():
                raise InvalidTreeMovement({'message': 'You can\'t move the root'})

            site.validate_relationship(right.get_parent(), self)
            self.node.move(right.node, pos='left')
        elif parent:
            site.validate_relationship(parent, self)
            self.node.move(parent.node, pos='last-child')
        else:
            assert right or parent

        try:
            # When moving, it's necessary to recheck compatibility for all of
            # our children. For example, this detects deep nesting of
            # un-nestable widgets.
            node = self._nodes.get()  # use a new, uncached node
            # use a prefetched tree
            node.prefetch_tree()
            node.content._recheck_children(site)
        except ParentChildRejection:
            # Backout. It'd be nice to rely on a transaction here and have this
            # happen automatically.
            if old_right_node:
                self.node.move(old_right_node, pos='left')
            else:
                self.node.move(old_parent_node, pos='last-child')
            raise

    def _recheck_children(self, site):
        for c in self.get_children():
            site.validate_relationship(self, c)
            c._recheck_children(site)

    @transaction.atomic
    def delete(self, raw=False):
        self.check_frozen()
        pre_delete_widget.send(self.__class__, instance=self, raw=raw)
        for child in self.get_children():
            child.delete(raw)
        self.node.delete()
        super(Content, self).delete()

    @transaction.atomic
    def clone(self):
        """
        **Note:** In order for clone to work, you need to have an
        auto-incrementing primary key.

        Also see https://docs.djangoproject.com/en/dev/topics/db/queries/#copying-model-instances
        """
        # TODO: Maybe provide support for many-to-many relationships too, or
        # document that you should provide your own clone()
        # See https://code.djangoproject.com/ticket/4027
        new = copy.copy(self)
        unset_pks(new)
        new.save()

        for f in self._meta.many_to_many:
            # This will only handle simple many-to-manies, those that don't
            # have a custom through table.
            f.save_form_data(new, f.value_from_object(self))

        return new

    def save(self, *args, **kwargs):
        self.check_frozen()
        return super(Content, self).save(*args, **kwargs)

    def check_frozen(self):
        if not self.pk:
            # if we don't have a pk, we can't have a node
            return
        try:
            self.node.check_frozen()
        except Node.DoesNotExist:
            pass

    def equal(self, other):
        return self.get_attributes() == other.get_attributes()


class UnknownWidget(Content):
    """
    A placeholder Content class used when the correct one can't be found. For
    example, when the database refers to widgets from an app that is no longer
    installed.
    """

    deletable = False
    draggable = False
    editable = False

    class Meta:
        app_label = 'widgy'
        # we don't actually need a db table
        managed = False

    def __init__(self, content_type, id, *args, **kwargs):
        super(UnknownWidget, self).__init__(*args, **kwargs)
        self.content_type = content_type
        self.id = id

    def render(self, *args, **kwargs):
        return ''

    def delete(*args, **kwargs):
        pass

    def warn(self):
        logger.warning('UnknownWidget being rendered. Content type: %s.%s',
                       self.content_type.app_label,
                       self.content_type.model)
