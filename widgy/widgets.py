from django.contrib.admin import widgets
from django.template.loader import render_to_string


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
