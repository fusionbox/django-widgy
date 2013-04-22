from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

import markdown

from widgy.utils import fancy_import, update_context

register = template.Library()


@register.simple_tag(takes_context=True)
def render(context, node):
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
def render_root(context, owner, field_name):
    """
    Renders `root_node` _unless_ `root_node_override` is in the context, in
    which case the override is rendered instead.

    `root_node_override` is used for stuff like preview, when a view wants to
    specify exactly what root node to use.
    """
    root_node = context.get('root_node_override')
    field = owner._meta.get_field_by_name(field_name)[0]
    with update_context(context, {'root_node_override': None}):
        return field.render(owner, context=context, node=root_node)
