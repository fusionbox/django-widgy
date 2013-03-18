import csv

from django.contrib import admin
from django.contrib.admin.util import unquote
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from .models import Form


class FormAdmin(admin.ModelAdmin):
    list_display = ('name', 'submission_count',)

    def has_add_permission(self, *args, **kwargs):
        return False

    def queryset(self, request):
        return self.model.objects.filter(_nodes__is_frozen=False).annotate_submission_count()

    def change_view(self, request, object_id, *args, **kwargs):
        obj = self.get_object(request, unquote(object_id))
        resp = HttpResponse(content_type='text/plain')

        values = obj.submissions.as_dictionaries()
        headers = obj.submissions.field_names()

        writer = csv.DictWriter(resp, list(headers))
        writer.writerow(headers)

        for row in values:
            writer.writerow(row)
        return resp

    def submission_count(self, obj):
        return obj.submission_count
    submission_count.short_description = _('submission count')

admin.site.register(Form, FormAdmin)
