from django.http import Http404
from django.views.generic import View
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ObjectDoesNotExist

from widgy.contrib.site_builder.models import WidgySite


class PageDetail(View):
    """
    TODO: This should probably be a middleware.  Catchall urls are gross and
    the middleware can allow pages to overide views conditionally.
    """
    def get_object(self):
        try:
            root_node = get_current_site(self.request).widgy_site.root_node
            content = root_node.content
        except (WidgySite.DoesNotExist, AttributeError):
            raise Http404

        try:
            return content.find_by_path(self.request.path)
        except ObjectDoesNotExist:
            raise Http404

    def get(self, *args, **kwargs):
        obj = self.get_object()
        return obj.render_to_response(self.request)

page_detail = PageDetail.as_view()
