import os

from django import forms
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string
from django.conf import settings

import bleach
from django_pyscss.scss import DjangoScss


PAGEDOWN_EDITOR_TEMPLATE = u'''
<div class="pagedown-buttonbar"></div>
{textarea}
<div class="pagedown-preview"></div>
'''


def scss_compile(scss_filename):
    scss = DjangoScss()
    css_content = scss.compile(scss_file=scss_filename)
    return css_content


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
        'toolbar': [
            {'name': 'clipboard', 'groups': ['clipboard', 'undo'], 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['HorizontalRule', 'SpecialChar']},
            {'name': 'justify', 'groups': ['justify'], 'items': ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'document', 'groups': ['mode', 'document', 'doctools'], 'items': ['Source']},
            {'name': 'tools', 'items': ['Maximize']},
            '/',
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup'], 'items': ['Bold', 'Italic', 'Strike', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'groups': ['list', 'indent', 'blocks', 'align'], 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote']},
            {'name': 'editing', 'groups': ['find', 'selection', 'spellchecker'], 'items': ['Scayt']},
            {'name': 'styles', 'items': ['Styles', 'Format']},
        ],
        'stylesSet': [
            {'name': 'Big', 'element': 'big'},
            {'name': 'Small', 'element': 'small'},
            {'name': 'Typewriter', 'element': 'tt'},

            {'name': 'Computer Code', 'element': 'code'},
            {'name': 'Keyboard Phrase', 'element': 'kbd'},
            {'name': 'Sample Text', 'element': 'samp'},
            {'name': 'Variable', 'element': 'var'},

            {'name': 'Deleted Text', 'element': 'del'},
            {'name': 'Inserted Text', 'element': 'ins'},

            {'name': 'Cited Work', 'element': 'cite'},
            {'name': 'Inline Quotation', 'element': 'q'},

            {'name': 'Language: RTL', 'element': 'span', 'attributes': {'dir': 'rtl'}},
            {'name': 'Language: LTR', 'element': 'span', 'attributes': {'dir': 'ltr'}},
        ],
        'removeButtons': '',
        'extraPlugins': 'justify',
        'justifyClasses': ['align-left', 'align-center', 'align-right', 'align-justify'],
        'indentClasses': ['text-indent-%d' % i for i in range(1,6)],
        'contentsCss': scss_compile('/widgy/page_builder/html.scss'),
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


class CKEditorField(forms.CharField):
    widget = CKEditorWidget

    ALLOWED_ATTRIBUTES = {
        '*': ['class', 'dir', 'title'],
        'a': ['href', 'target', 'rel', 'name'],
        'time': ['datetime', 'pubdate'],
        'img': ['src'],

        'table': ['border'],
        'colgroup': ['span'],
        'col': ['span'],
        'td': ['colspan', 'rowspan', 'headers'],
        'th': ['colspan', 'rowspan', 'headers', 'scope'],
    }
    ALLOWED_TAGS = [
        'a', 'abbr', 'acronym', 'address', 'b', 'big', 'br', 'cite', 'code',
        'del', 'dfn', 'div', 'em', 'hr', 'i', 'ins', 'kbd', 'mark', 'p', 'pre',
        'q', 'samp', 'small', 'span', 'strong', 'sub', 'sup', 'time', 'u',
        'var', 'wbr', 's', 'tt',

        'ul', 'ol', 'li',

        'dl', 'dt', 'dd',

        'blockquote', 'details', 'summary',

        'hgroup', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',

        'figure', 'figcaption', 'img',

        'caption', 'col', 'colgroup', 'table', 'tbody', 'td', 'tfoot', 'th',
        'thead', 'tr',
    ]

    def clean(self, value):
        value = super(CKEditorField, self).clean(value)
        return bleach.clean(value,
                            tags=self.ALLOWED_TAGS,
                            attributes=self.ALLOWED_ATTRIBUTES)


class MiniCKEditorWidget(CKEditorWidget):
    CONFIG = {
        'toolbar': [
            {'name': 'basicstyles', 'groups': ['basicstyles', 'cleanup'], 'items': ['Bold', 'Italic', 'Strike', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'undo', 'groups': ['undo'], 'items': ['Undo', 'Redo']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'mode', 'groups': ['mode'], 'items': ['Source']},
            {'name': 'editing', 'groups': ['find', 'selection', 'spellchecker'], 'items': ['Scayt']},
        ],
        'contentsCss': scss_compile('/widgy/page_builder/html.scss')
    }


class MiniCKEditorField(forms.CharField):
    widget = MiniCKEditorWidget
