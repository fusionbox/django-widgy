from mezzanine.pages.views import page as page_view

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
