from django import forms


PAGEDOWN_EDITOR_TEMPLATE = '''
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

        return PAGEDOWN_EDITOR_TEMPLATE.format(textarea=textarea)


class MarkdownField(forms.CharField):
    widget = MarkdownWidget
