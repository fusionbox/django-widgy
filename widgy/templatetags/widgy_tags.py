from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

import markdown

from widgy.utils import fancy_import, update_context

register = template.Library()

class RenderNode(template.Node):
    def __init__(self, arg):
        self.arg = template.Variable(arg)

    def render(self, context):
        try:
            node = self.arg.resolve(context)
        except template.VariableDoesNotExist as e:
            raise Exception(e)
        return node.render(context)

@register.tag
def render(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError("Usage: {% render node %}")
    return RenderNode(bits[1])

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


class RenderRootNode(template.Node):
    def __init__(self, obj, field_name):
        self.obj = template.Variable(obj)
        self.field_name = template.Variable(field_name)

    def render(self, context):
        try:
            owner = self.obj.resolve(context)
            field_name = self.field_name.resolve(context)
        except template.VariableDoesNotExist as e:
            raise Exception(e)
        return render_root(context, owner, field_name)

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

@register.tag(name='render_root')
def render_root_tag(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            "Usage: {% render_root owner 'widgy_field_name' %}"
        )

    return RenderRootNode(bits[1], bits[2])
