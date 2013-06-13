from django.contrib.admin import widgets
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.contrib.admin.templatetags.admin_static import static
from django.core import urlresolvers
from widgy.utils import format_html

from django.utils.safestring import mark_safe


class DateTimeMixin(object):
    class Media:
        extend = False
        js = tuple()

    def render(self, name, value, attrs=None):
        widget = super(DateTimeMixin, self).render(name, value, attrs)
        return render_to_string('page_builder/datetime_widget.html', {
            'widget': widget,
        })


class DateTimeWidget(DateTimeMixin, widgets.AdminSplitDateTime):
    pass


class DateWidget(DateTimeMixin, widgets.AdminDateWidget):
    pass


class TimeWidget(DateTimeMixin, widgets.AdminTimeWidget):
    pass


class RelatedFieldWidgetWrapper(widgets.RelatedFieldWidgetWrapper):
    """
    Like the admin RelatedFieldWidgetWrapper, but adds a link to the
    edit page of the related object.

    Based on <http://djangosnippets.org/snippets/2562/>
    """
    class Media:
        js = ('widgy/js/related-widget-wrapper.js',)

    def __init__(self, *args, **kwargs):
        self.can_change_related = kwargs.pop('can_change_related', None)
        super(RelatedFieldWidgetWrapper, self).__init__(*args, **kwargs)

    def get_change_url(self, rel_to, info, args=[]):
        return urlresolvers.reverse("admin:%s_%s_change" % info,
                                    current_app=self.admin_site.name,
                                    args=args)

    def render(self, name, value, attrs={}, *args, **kwargs):
        attrs['class'] = ' '.join((attrs.get('class', ''), 'related-widget-wrapper'))
        parts = [
            super(RelatedFieldWidgetWrapper, self).render(name, value, attrs, *args, **kwargs)
        ]
        rel_to = self.rel.to
        info = (rel_to._meta.app_label, rel_to._meta.module_name)

        if self.can_change_related and value:
            change_url = self.get_change_url(rel_to, info, [value])
            parts.append(format_html(
                '<a href="{change_url}" id="change_id_{name}" '
                '   class="related-widget-wrapper-link related-widget-wrapper-change-link"'
                '   data-href-template="{template}">'
                '  <img src="{img}" width="10" height="10" alt="{alt}"/>'
                '</a>',
                change_url=change_url,
                name=name,
                img=static('admin/img/icon_changelink.gif'),
                alt=_('Edit'),
                template=self.get_change_url(rel_to, info, ['%s']),
            ))

        return mark_safe(''.join(parts))
