from django import forms
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string


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


class CKEditorWidget(forms.Textarea):
    CONFIG = {
    }

    def __init__(self, *args, **kwargs):
        super(CKEditorWidget, self).__init__(*args, **kwargs)
        self.attrs['class'] = 'widgy_ckeditor'

    def render(self, name, value, attrs=None):
        textarea = super(CKEditorWidget, self).render(name, value, attrs)
        return render_to_string('page_builder/ckeditor_widget.html', {
            'html_id': attrs['id'],
            'textarea': textarea,
            'ckeditor_path': staticfiles_storage.url('widgy/js/lib/ckeditor/'),
            'config': self.CONFIG,
        })
