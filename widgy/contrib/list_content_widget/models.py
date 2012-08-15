from widgy.models import Content


class ListContentBase(Content):
    """
    Abstract Baseclass for listing a queryset.

    It is up to the developer to inherit this class and implement their own
    list content.
    """
    model = None
    paginate_by = None
    queryset = None
    template_name = None

    class Meta:
        abstract = True

    def get_queryset(self):
        """
        Gets the class queryset, if defined.  Otherwise, use the default model
        manager.

        Overwrite this method to return a custom queryset.
        """
        return self.queryset or self.model._default_manager.all()

    def get_context(self):
        """
        """
        return {
                'list': self.get_queryset(),
                'paginate_by': self.paginate_by,
                }

    def render(self, context):
        """
        """
        context.update(self.get_context())
        return super(ListContentBase, self).render(context)

    def get_templates(self):
        """
        """
        templates = (
            'list_content.html',
            )
        return templates
