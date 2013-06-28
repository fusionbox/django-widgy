import csv

from django.contrib import admin
from django.contrib.admin.util import unquote
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns, url
from django.template.defaultfilters import slugify

from widgy.utils import force_text

from .models import Form


class FormAdmin(admin.ModelAdmin):
    list_display = ('name', 'submission_count',)

    def has_add_permission(self, *args, **kwargs):
        return False

    def queryset(self, request):
        return self.model.objects.filter(_nodes__is_frozen=False).annotate_submission_count()

    def get_urls(self, *args, **kwargs):
        urls = super(FormAdmin, self).get_urls(*args, **kwargs)
        info = self.model._meta.app_label, self.model._meta.module_name
        return urls + patterns('',
                               url(r'^(.+).csv$',
                                   self.admin_site.admin_view(self.download_view),
                                   name='%s_%s_download' % info),
                               )

    def change_view(self, request, object_id, *args, **kwargs):
        obj = self.get_object(request, unquote(object_id))
        opts = self.model._meta

        headers = obj.submissions.get_formfield_labels()
        rows = obj.submissions.as_ordered_dictionaries(headers.keys())
        return render(request, 'admin/form_builder/form/change_form.html', {
            'title': _('View %s submissions') % force_text(opts.verbose_name),
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'app_label': opts.app_label,
            'headers': headers,
            'rows': rows,
            'csv_file_name': self.csv_file_name(obj),
        })

    def csv_file_name(self, obj):
        # slugify not only for readability, but for header injection as well.
        return '%s-submissions.csv' % slugify(obj.name)

    def download_view(self, request, object_id, *args, **kwargs):
        obj = self.get_object(request, unquote(object_id))
        resp = HttpResponse(content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="%s"' % self.csv_file_name(obj)

        obj.submissions.to_csv(resp)

        return resp

    def submission_count(self, obj):
        return obj.submission_count
    submission_count.short_description = _('submission count')

admin.site.register(Form, FormAdmin)
