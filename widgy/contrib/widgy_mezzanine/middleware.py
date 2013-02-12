from mezzanine.pages.views import page as page_view
from mezzanine.pages.models import Page
from mezzanine.utils.urls import path_to_slug

from fusionbox.middleware import GenericTemplateFinderMiddleware


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
