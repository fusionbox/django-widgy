from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

import markdown

from widgy.utils import fancy_import

register = template.Library()


@register.simple_tag(takes_context=True)
def render(context, node):
    from widgy.models import Content

    assert 'request' in context, "Widgy rendering requires that request is in context."

    if isinstance(node, Content):
        node = node.node
    elif hasattr(node, 'get_published_node'):
        node = node.get_published_node(context['request'])

    if not node:
        return 'no content'

    node.maybe_prefetch_tree()

    return node.render(context)


@register.filter
def scss_files(site):
    try:
        site = getattr(settings, site)
    except AttributeError:
        pass

    site = fancy_import(site)

    return site.scss_files


@register.filter
def js_files(site):
    try:
        site = getattr(settings, site)
    except AttributeError:
        pass

    site = fancy_import(site)

    return site.js_files


@register.filter(name='markdown')
def mdown(value):
    value = markdown.markdown(
        value,
        extensions=['sane_lists'],
        safe_mode='escape',
    )

    return mark_safe(value)

@register.simple_tag(takes_context=True)
def render_root(context, root_node):
    """
    Renders `root_node` _unless_ `root_node_override` is in the context, in
    which case the override is rendered instead.

    `root_node_override` is used for stuff like preview, when a view wants to
    specify exactly what root node to use.
    """
    try:
        root_node = context['root_node_override']
    except KeyError:
        pass
    return render(context, root_node)
