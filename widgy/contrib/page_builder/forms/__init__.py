from django import forms
from django.utils.safestring import mark_safe


PAGEDOWN_EDITOR_TEMPLATE = u'''
<div class="pagedown-buttonbar"></div>
{textarea}
<div class="pagedown-preview"></div>
'''


class MarkdownWidget(forms.Textarea):
    class Media:
        css = {
            'all': ('widgy/js/components/markdown/lib/pagedown.css',),
        }

    def render(self, *args, **kwargs):
        textarea = super(MarkdownWidget, self).render(*args, **kwargs)

        return mark_safe(PAGEDOWN_EDITOR_TEMPLATE.format(textarea=textarea))


class MarkdownField(forms.CharField):
    widget = MarkdownWidget
