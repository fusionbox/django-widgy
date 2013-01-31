from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def render(context, node):
    from widgy.models import Content

    assert 'request' in context, "Widgy rendering requires that request is in context."

    if isinstance(node, Content):
        node = node.node
    elif hasattr(node, 'get_published_node'):
        node = node.get_published_node(context['request'])

    node.maybe_prefetch_tree()

    return node.render(context)
