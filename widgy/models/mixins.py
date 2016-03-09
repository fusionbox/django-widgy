from __future__ import unicode_literals

from operator import attrgetter

import six


class DefaultChildrenMixin(object):
    """
    With this mixin, you can specify which children your Content will have.  It
    provides a post_create that will add the children for you and also a
    valid_parent_of that does validation.  Specify the children like this:

        default_children = [
            (MainContent, (), {}),
            (Sidebar, (), {}),
        ]

    such that index 0 is the content class and 1 and 2 are the args and kwargs
    to be passed in during post_create.
    """
    default_children = tuple()

    def post_create(self, site):
        for cls, args, kwargs in self.default_children:
            self.add_child(site, cls, *args, **kwargs)


class StrictDefaultChildrenMixin(DefaultChildrenMixin):
    """
    StrictDefaultChildrenMixin works slightly differently from
    DefaultChildrenMixin, in that it also provides validation to ensure that
    only those children specified in default_children are compatible.

    It also provides a property called children that provides named access to
    the children.  You have to specify the children like this.

        default_children = [
            ('main', MainContent, (), {}),
            ('sidebar', Sidebar, (), {}),
        ]
    """
    def post_create(self, site):
        for name, cls, args, kwargs in self.default_children:
            self.add_child(site, cls, *args, **kwargs)

    @property
    def children(self):
        return dict(
            (self.default_children[index][0], child) for index, child in enumerate(self.get_children())
        )

    def valid_parent_of(self, cls, obj=None):
        if obj and obj in self.get_children():
            return True

        return (issubclass(cls, tuple([child_class[1] for child_class in self.default_children])) and
                len(self.get_children()) < len(self.default_children))


class InvisibleMixin(object):
    """
    Provides a preview template that accepts children, but is otherwise
    invisible.
    """
    def get_css_classes(self):
        return super(InvisibleMixin, self).get_css_classes() + ('invisibleBucket',)

    @classmethod
    def get_template_kwargs(cls, **kwargs):
        defaults = {
            'app_label': 'mixins',
            'model_name': 'invisible',
        }
        defaults.update(**kwargs)

        return super(InvisibleMixin, cls).get_template_kwargs(**kwargs) + [defaults]


class TabbedContainer(object):
    component_name = 'tabbed'

    def get_css_classes(self):
        return super(TabbedContainer, self).get_css_classes() + ('tabbed',)

    @classmethod
    def get_template_kwargs(cls, **kwargs):
        defaults = {
            'app_label': 'mixins',
            'model_name': 'tabbed',
        }
        defaults.update(**kwargs)

        return super(TabbedContainer, cls).get_template_kwargs(**kwargs) + [defaults]


def DisplayNameMixin(fn):
    """
    Helper for making nicer display names.  Example usage:

        class Thing(DisplayNameMixin(lambda x: x.title), Content):
            ...

        thing = Thing()
        thing.display_name  # Thing
        thing.title = 'Title'
        thing.display_name  # Thing - title
    """
    class cls(object):
        def deconstruct(self):
            return 'widgy.models.mixins.DisplayNameMixin', (fn,), {}

        @property
        def display_name(self):
            name = super(cls, self).display_name
            extra = fn(self)
            if extra:
                name = '%s - %s' % (name, extra)

            return name

    return cls


TitleDisplayNameMixin = DisplayNameMixin(attrgetter('title'))
StrDisplayNameMixin = DisplayNameMixin(six.text_type)

# for migration serialization
TitleDisplayNameMixin.__name__ = str('TitleDisplayNameMixin')
StrDisplayNameMixin.__name__ = str('StrDisplayNameMixin')
