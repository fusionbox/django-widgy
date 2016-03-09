from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

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
    import markdown
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
    field = owner._meta.get_field(field_name)
    with update_context(context, {'root_node_override': None}):
        return field.render(owner, context=context, node=root_node)


@register.simple_tag
def reverse_site_url(site, view_string, *args, **kwargs):
    """
    We would be tempted to use
        {% url site.view kwarg=value kwarg2=value2 %}
    but site.view actually returns a callable (the view itself). The Django
    template variable resolver tries to call it, which fails and resolves
    `site.view' as an empty string.
    """
    view = getattr(site, view_string)
    return site.reverse(view, args=args, kwargs=kwargs)


@register.assignment_tag(takes_context=True)
def has_change_permission(context, site, obj):
    return site.has_change_permission(context['request'], obj)


@register.assignment_tag(takes_context=True)
def has_add_permission(context, site, parent, obj):
    created_obj_cls = type(obj)
    return site.has_add_permission(context['request'], parent, created_obj_cls)


@register.assignment_tag(takes_context=True)
def has_delete_permission(context, site, obj):
    return site.has_delete_permission(context['request'], obj)


@register.assignment_tag
def get_action_links(owner, root_node):
    try:
        get_action_links = owner.get_action_links
    except AttributeError:
        return []
    else:
        return get_action_links(root_node)
