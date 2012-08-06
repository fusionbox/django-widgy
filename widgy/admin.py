import operator
from copy import deepcopy

from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.db.models import Q

from mezzanine.generic.models import ThreadedComment
from mezzanine.pages.models import RichTextPage
from mezzanine.pages.admin import PageAdmin

from widgy.models import ContentPage


class WidgyPageAdmin(PageAdmin):
    widgy_fields = None

    #add_form_template = 'admin/widgy/change_form.html'
    change_form_template = 'admin/widgy/change_form.html'

    def __init__(self, *args, **kwargs):
        """
        Creates a list of foreign key fields that point to Node instances.
        """
        super(WidgyPageAdmin, self).__init__(*args, **kwargs)
        if self.widgy_fields is None:
            widgy_fields = dict([(f.name, f.verbose_name) for f in self.model.get_node_fields()])
            self.widgy_fields = widgy_fields or None

        if self.exclude is None and self.widgy_fields:
            self.exclude = self.widgy_fields.keys()

    def get_readonly_fields(self, request, obj=None):
        """
        Ensures that widgy fields are excluded from the form and admin interface.
        """
        readonly_fields = list(super(WidgyPageAdmin, self).get_readonly_fields(request, obj))
        if self.widgy_fields:
            for field_name in self.widgy_fields:
                readonly_fields.append(field_name)
        return tuple(set(readonly_fields))

    def get_form(self, request, obj=None, **kwargs):
        """
        Dynamically adds fields to the create form for selecting which layouts
        any widgy fields should use
        """
        form = super(WidgyPageAdmin, self).get_form(request, obj, **kwargs)
        if self.widgy_fields and obj is None:
            layouts = self.model.get_valid_layouts()
            qs = [Q(app_label=c._meta.app_label, model=c._meta.module_name) for c in layouts]
            layout_qs = ContentType.objects.filter(reduce(operator.or_, qs))
            for field_name, field_title in self.widgy_fields.iteritems():
                form.base_fields[field_name + '_layout'] = forms.ModelChoiceField(label=field_title.title() + ' Layout', queryset=layout_qs)
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(WidgyPageAdmin, self).get_fieldsets(request, obj)
        if not obj and self.widgy_fields:
            # Don't override the declared fieldsets
            fieldsets = deepcopy(fieldsets)
            for field_name in self.widgy_fields:
                if field_name + '_layout' not in fieldsets[0][1]['fields']:
                    fieldsets[0][1]['fields'].append(field_name + '_layout')

        # https://github.com/stephenmcd/mezzanine/pull/354
        if self.widgy_fields:
            for field_name in self.widgy_fields:
                try:
                    fieldsets[0][1]['fields'].remove('root_node')
                except ValueError:
                    pass

        return fieldsets

    def save_model(self, request, obj, form, change):
        if not change and self.widgy_fields:
            for field_name in self.widgy_fields:
                root_node = form.cleaned_data[field_name + '_layout'].model_class().add_root().node
                setattr(obj, field_name, root_node)
        super(WidgyPageAdmin, self).save_model(request, obj, form, change)

admin.site.register(ContentPage, WidgyPageAdmin)
admin.site.unregister(RichTextPage)
admin.site.unregister(ThreadedComment)
admin.site.unregister(Group)
