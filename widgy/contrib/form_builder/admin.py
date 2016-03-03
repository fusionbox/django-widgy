from django.contrib import admin
try:
    from django.contrib.admin.utils import unquote
except ImportError:  # < Django 1.8
    from django.contrib.admin.util import unquote
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from django.template.defaultfilters import slugify
from django.http import Http404
from django.utils.html import escape
from django.utils.encoding import force_text

from .models import Form


class FormAdmin(admin.ModelAdmin):
    list_display = ('name', 'submission_count',)

    def has_add_permission(self, *args, **kwargs):
        return False

    def get_queryset(self, request):
        return self.model.objects.filter(_nodes__is_frozen=False).annotate_submission_count()

    @property
    def download_url_name(self):
        return '{0}_{1}_download'.format(
            self.model._meta.app_label,
            self.model._meta.model_name,
        )

    def get_urls(self, *args, **kwargs):
        urls = super(FormAdmin, self).get_urls(*args, **kwargs)
        return urls + [
            url(r'^(.+).csv$',
                self.admin_site.admin_view(self.download_view),
                name=self.download_url_name,
                ),
        ]

    def change_view(self, request, object_id, *args, **kwargs):
        obj = self.get_object(request, unquote(object_id))
        opts = self.model._meta

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(opts.verbose_name), 'key': escape(object_id)})


        headers = obj.submissions.get_formfield_labels()
        rows = obj.submissions.as_ordered_dictionaries(headers.keys())
        return render(request, 'admin/form_builder/form/change_form.html', {
            'title': _('View %s submissions') % force_text(opts.verbose_name),
            'object_id': object_id,
            'original': obj,
            'is_popup': ('_popup' in request.POST or
                         '_popup' in request.GET),
            'app_label': opts.app_label,
            'opts': opts,
            'headers': headers,
            'rows': rows,
            'csv_file_name': self.csv_file_name(obj),
            'download_url': reverse('admin:{0}'.format(self.download_url_name), args=[object_id])
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
