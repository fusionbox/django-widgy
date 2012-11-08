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
def render(context, content):
    # AttributeError is consumed by the templating engine so we make it an
    # AssertionError
    assert hasattr(content, 'render')
    assert 'request' in context, "Widgy rendering requires that request is in context."
    if not hasattr(content, '_children'):
        content.prefetch_tree()

    return content.render(context)
