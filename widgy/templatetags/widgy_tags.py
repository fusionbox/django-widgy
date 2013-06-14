from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template import TemplateSyntaxError, Node
from django.core.exceptions import PermissionDenied

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


@register.simple_tag
def reverse_site_url(site, view_string, *args, **kwargs):
    """We would be tempted to put
        {% url site.view kwarg=value kwarg2=value2 %}
    but site.view actually return a callable (the view itself).
    And Django template variable tries solver call it, fails
    and resolve `site.view' as an empty string.
    """
    view = getattr(site, view_string)
    return site.reverse(view, args=args, kwargs=kwargs)


class SitepermsWrapper(object):

    def __init__(self, request, site):
        self._request = request
        self._site = site

    def __getitem__(self, item):
        try:
            view = getattr(self._site, item)
            view_instance = self._site.get_view_instance(view)
            self._site.authorize(self._request, view_instance)
            return True
        except (AttributeError, ValueError):
            # View does not exists, either getattr or
            # get_view_instance has failed
            raise KeyError
        except PermissionDenied:
            return False


class SitepermsNode(Node):

    def __init__(self, site, siteperms):
        self.site = site
        self.siteperms = siteperms

    def render(self, context):
        if self.site not in context:
            raise TemplateSyntaxError(("'siteperms' variable %s "
                                       "not in context") % self.site)
        if self.siteperms in context:
            raise TemplateSyntaxError(("'siteperms' overriding variable "
                                       "%s") % self.site)
        context[self.siteperms] = SitepermsWrapper(context['request'],
                                                   context[self.site])
        return ''


@register.tag
def siteperms(parser, token):
    bits = token.split_contents()
    # TODO: Support for permissions on one specific object
    # {% siteperms site as variable %}
    # {% siteperms site as variable with object %}
    # {% siteperms site with object as variable %}
    if len(bits) != 4 and bits[2] != 'as':
        raise TemplateSyntaxError("'siteperms' syntax should be "
                                  "{% siteperms site as variable %}")
    site = bits[1]
    siteperms = bits[3]
    return SitepermsNode(site, siteperms)
