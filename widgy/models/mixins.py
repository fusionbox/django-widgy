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
    def valid_parent_of(self, cls, obj=None):
        if obj and obj in self.children:
            return True

        return (issubclass(cls, tuple([child_class[0] for child_class in self.default_children])) and
                len(self.children) < len(self.default_children))


class InvisibleMixin(object):
    """
    Provides a preview template that accepts children, but is otherwise
    invisible.
    """
    css_classes = ('invisible',)

    @classmethod
    def get_template_kwargs(cls, **kwargs):
        defaults = {
            'app_label': 'mixins',
            'module_name': 'invisible',
        }
        defaults.update(**kwargs)

        return defaults
