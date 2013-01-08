from django import template

register = template.Library()


class VerbatimNode(template.Node):
    def __init__(self, content):
        self.content = content

    def render(self, context):
        return self.content


@register.tag
def verbatim(parser, token):
    """
    Stops the template engine from rendering the contents of this block tag.

    Usage::

        {% verbatim %}
            {% don't process this %}
        {% endverbatim %}

    You can also designate a specific closing tag block (allowing the
    unrendered use of ``{% endverbatim %}``)::

        {% verbatim myblock %}
            ...
        {% endverbatim myblock %}
    """
    nodelist = parser.parse(('endverbatim',))
    parser.delete_first_token()
    return VerbatimNode(nodelist.render(template.Context()))


@register.simple_tag(takes_context=True)
def render(context, node):
    from widgy.models import Node

    if not isinstance(node, Node):
        node = node.node

    assert 'request' in context, "Widgy rendering requires that request is in context."
    node.maybe_prefetch_tree()

    return node.render(context)
