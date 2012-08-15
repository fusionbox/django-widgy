from django.db.models import CharField
from widgy.models import Content


class ListContentBase(Content):
    """
    Abstract Baseclass for listing a queryset.

    It is up to the developer to inherit this class and implement their own
    list content.

    If the default manager will be used, you can just set the `model` class
    property to the Django model you wish to callout.

    If you need a more complex query, you may override the `queryset` class
    property.  If the queryset needs knowledge of the model instance, there is
    a `get_queryset` method that is available.
    """
    model = None
    queryset = None
    limit = 3
    component_name = "widgy.listcontentbase"

    header = CharField(max_length=255, blank=True, default="")

    class Meta:
        abstract = True

    def get_queryset(self):
        """
        Gets the class queryset, if defined.  Otherwise, use the default model
        manager.

        Overwrite this method to return a custom queryset.
        """
        return self.queryset or self.model._default_manager.all()[:self.limit]

    def get_context(self):
        """
        """
        return {'list': self.get_queryset()}

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

    def to_json(self):
        json = super(ListContentBase, self).to_json()
        list_tojson = [item.__unicode__() for item in self.get_queryset()]
        json['list'] = list_tojson
        json['header'] = self.header
        return json
