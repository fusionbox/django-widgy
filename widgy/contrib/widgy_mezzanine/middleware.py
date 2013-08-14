from django.conf import settings
from django.template import TemplateDoesNotExist
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.core import urlresolvers

from mezzanine.pages.views import page as page_view
from mezzanine.pages.models import Page
from mezzanine.utils.urls import path_to_slug

@requires_csrf_token
def generic_template_finder_view(request, base_path='', extra_context={}):
    """
    Find a template based on the request url and render it.

    * ``/`` -> ``index.html``
    * ``/foo/`` -> ``foo.html`` OR ``foo/index.html``
    """
    path = base_path + request.path
    if not path.endswith('/'):
        path += '/'
    possibilities = (
            path.strip('/') + '.html',
            path.lstrip('/') + 'index.html',
            path.strip('/'),
            )
    for t in possibilities:
        try:
            response = render(request, t, extra_context)
        except TemplateDoesNotExist:
            continue
        if t.endswith('.html') and not path.endswith(request.path) and settings.APPEND_SLASH:
            # Emulate what CommonMiddleware does and redirect, only if:
            # - the template we found ends in .html
            # - the path has been modified (slash appended)
            # - and settings.APPEND_SLASH is True
            return HttpResponsePermanentRedirect(path)
        return response
    raise Http404('Template not found in any of %r' % (possibilities,))


class GenericTemplateFinderMiddleware(object):
    """
    GenericTemplateFinderMiddleware won't intercept requests that had a view.
    This version exempts mezzanine.pages.views.page from this check.
    """

    def process_view(self, request, view_func, *args, **kwargs):
        """
        Informs :func:`process_response` that there was a view for this url and that
        it threw a real 404.
        """
        if view_func != page_view:
            request._generic_template_finder_middleware_view_found = True

    def process_response(self, request, response):
        """
        Ensures that
        404 raised from view functions are not caught by
        ``GenericTemplateFinderMiddleware``.
        """
        if response.status_code == 404 and not getattr(request, '_generic_template_finder_middleware_view_found', False):
            try:
                if hasattr(request, 'urlconf'):
                    # Django calls response middlewares after it has unset the
                    # request's urlconf. Set it temporarily so the template can
                    # reverse properly.
                    urlresolvers.set_urlconf(request.urlconf)
                return generic_template_finder_view(request, extra_context=self.get_extra_context(request))
            except Http404:
                return response
            except UnicodeEncodeError:
                return response
            finally:
                urlresolvers.set_urlconf(None)
        else:
            return response


    def get_extra_context(self, request):
        """
        Informs :func:`process_response` that there was a view for this url and that
        it threw a real 404.
        """
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
