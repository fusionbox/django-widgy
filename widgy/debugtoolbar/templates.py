from django.dispatch import Signal
from django.template.loader import select_template, TemplateDoesNotExist
from django.contrib.staticfiles import finders

from debug_toolbar.panels import DebugPanel

from widgy.models import Content

template_hierarchy_called = Signal(providing_args=['cls', 'kwargs', 'templates', 'used'])


def unique_list(lst):
    """
    Removes duplicates from a list while preserving order
    """
    res = []
    for i, item in enumerate(lst):
        if i == len(lst) - 1 or lst[i + 1] != item:
            res.append(item)
    return res

# Monkey patch in our own, instrumented, get_templates_hierarchy. Make sure to
# keep it a classmethod.
old_get_templates_hierarchy_unbound = Content.get_templates_hierarchy.im_func

def new_get_templates_hierarchy(cls, **kwargs):
    res = old_get_templates_hierarchy_unbound(cls, **kwargs)
    res = unique_list(res)
    try:
        name = select_template(res).name
    except TemplateDoesNotExist:
        name = [i for i in res if finders.find(i)]
    template_hierarchy_called.send(sender=cls, cls=cls, kwargs=kwargs, templates=res, used=name)
    return res
Content.get_templates_hierarchy = classmethod(new_get_templates_hierarchy)


class TemplatePanel(DebugPanel):
    name = 'Widgy templates'
    template = 'widgy/debugtoolbar/templates.html'

    def __init__(self, *args, **kwargs):
        super(TemplatePanel, self).__init__(*args, **kwargs)
        template_hierarchy_called.connect(self._store_info)
        self.calls = []

    def nav_title(self):
        return 'Widgy templates'

    def _store_info(self, **kwargs):
        # A class can't be outputted directly in a template, because it's
        # callable. `_meta` can't be accessed because it starts with an
        # underscore.
        kwargs['cls_name'] = '%s.%s' % (kwargs['cls']._meta.app_label,
                                        kwargs['cls'].__name__)
        self.calls.append(kwargs)

    def process_response(self, request, response):
        self.record_stats({
            'calls': self.calls,
        })

    def url(self):
        return ''

    def title(self):
        return '%s widgets rendered' % len(self.calls)

    @property
    def has_content(self):
        return bool(self.calls)
