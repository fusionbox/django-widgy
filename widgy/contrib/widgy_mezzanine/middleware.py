from urlparse import urlparse

from django.conf import settings
from django.contrib.sites.models import get_current_site

from mezzanine.pages.views import page as page_view
from mezzanine.pages.models import Page
from mezzanine.utils.urls import path_to_slug

from fusionbox.middleware import (
    GenericTemplateFinderMiddleware, RedirectFallbackMiddleware, get_redirect)


class GenericTemplateFinderMiddleware(GenericTemplateFinderMiddleware):
    """
    GenericTemplateFinderMiddleware won't intercept requests that had a view.
    This version exempts mezzanine.pages.views.page from this check.
    """
    def process_view(self, request, view_func, *args, **kwargs):
        if view_func != page_view:
            return super(GenericTemplateFinderMiddleware, self).process_view(
                request, view_func, *args, **kwargs)

    def get_extra_context(self, request):
        slug = path_to_slug(request.path_info)
        # Links may have slugs that begin and end in '/'
        parts = slug.split("/")
        slugs = ["/".join(parts[:i]) for i in range(1, len(parts) + 1)]
        slugs = ['/' + i + '/' for i in slugs] + slugs

        pages = Page.objects.published(
            for_user=request.user,
            include_login_required=True
        ).filter(
            slug__in=slugs
        ).order_by(
            '-slug'
        )

        if pages:
            page = pages[0]
            context = {
                'page': page,
                '_current_page': page,
            }
            page.set_helpers(context)
            return context
        else:
            return {}


class RedirectFallbackMiddleware(RedirectFallbackMiddleware):
    def process_response(self, request, response):
        is_404 = response.status_code == 404
        is_my_site = get_current_site(request).domain == request.get_host()

        # Mezzanine has a urlpattern for all urls that end in a slash, so
        # CommonMiddleware redirects all 404s. We still need to check for a
        # redirect in this case.
        is_common_redirect = False
        if settings.APPEND_SLASH and response.status_code == 301:
            parsed = urlparse(response['Location'])
            if parsed.path == request.path_info + '/':
                is_common_redirect = True

        if (is_404 or not is_my_site) or is_common_redirect:
            path = request.get_full_path()
            full_uri = request.build_absolute_uri()
            response = get_redirect(self.redirects, path, full_uri) or response
        return response
