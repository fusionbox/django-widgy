from django.db import models
from django import forms

from south.modelsinspector import add_introspection_rules


class WYMEditorArea(forms.Textarea):
    def __init__(self, attrs=None):
        attrs = attrs or {}
        base_class = attrs.get("class", "")
        attrs['class'] = " ".join((base_class, "WYMEditor",))
        super(WYMEditorArea, self).__init__(attrs=attrs)

    class Media:
        css = {
            "all": (
                "//ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/smoothness/jquery-ui.css",
                'wymeditor/skins/twopanels/skin.css',
            )
        }
        js = (
            'js/load_wymeditor.js',
        )


class WYMEditorField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'widget': WYMEditorArea}
        defaults.update(kwargs)
        return super(WYMEditorField, self).formfield(**defaults)


add_introspection_rules([], ["^widgy\.contrib\.page_builder\.wymeditor\.WYMEditorField"])
