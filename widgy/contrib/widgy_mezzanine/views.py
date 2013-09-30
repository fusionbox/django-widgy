from django.db.models import Q
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponsePermanentRedirect,
)
from django.utils.http import is_safe_url

from mezzanine.pages.views import page as page_view
from mezzanine.pages.models import Page

from widgy.contrib.form_builder.views import HandleFormMixin
from widgy.contrib.widgy_mezzanine import get_widgypage_model
from widgy.models import Node
from widgy.views.base import AuthorizedMixin
from widgy.utils import fancy_import

WidgyPage = get_widgypage_model()


def get_page_from_node(node):
    root_node = node.get_root()
    try:
        # try to find a page that uses this root node
        return WidgyPage.objects.distinct().get(
            Q(root_node__commits__root_node=root_node) | Q(root_node__working_copy=root_node)
        )
    except WidgyPage.DoesNotExist:
        # otherwise, use a fake page
        return WidgyPage(
            titles='restoring page',
            content_model='widgypage',
        )


class PageViewMixin(object):
    def get_page(self):
        try:
            return Page.objects.published(for_user=self.request.user).get(slug=self.kwargs['slug'])
        except (KeyError, Page.DoesNotExist):
            # restoring, use a fake page
            return WidgyPage(
                titles='restoring page',
                content_model='widgypage',
            )


class HandleFormView(HandleFormMixin, PageViewMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            if not is_safe_url(request.GET['from']):
                return HttpResponseForbidden()
            return HttpResponsePermanentRedirect(request.GET['from'])
        except KeyError:
            return HttpResponseBadRequest()

    def form_invalid(self, form):
        root_node = self.form_node.get_root()
        page = self.get_page()

        return page_view(self.request, page.slug, extra_context=self.get_context_data(
            form=form,
            page=page,
            root_node_override=root_node,
        ))

handle_form = HandleFormView.as_view()


class PreviewView(AuthorizedMixin, SingleObjectMixin, PageViewMixin, View):
    model = Node
    pk_url_kwarg = 'node_pk'

    def get(self, request, *args, **kwargs):
        node = self.get_object()
        page = self.get_page()

        context = {
            'page': page,
            'root_node_override': node,
            '_current_page': page,
        }

        return page_view(request, page.slug, extra_context=context)

preview = PreviewView.as_view(
    site=fancy_import(settings.WIDGY_MEZZANINE_SITE),
)
