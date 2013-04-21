from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.http import Http404
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from mezzanine.pages.views import page as page_view

from widgy.contrib.widgy_mezzanine.models import WidgyPage
from widgy.models import Node


def get_page_from_node(node):
    root_node = node.get_root()
    try:
        # try to find a page that uses this root node
        return get_object_or_404(
            WidgyPage.objects.distinct(),
            Q(root_node__commits__root_node=root_node) | Q(root_node__working_copy=root_node)
        ).page_ptr
    except Http404:
        # otherwise, use a fake page
        return WidgyPage(
            titles='restoring page',
            content_model='widgypage',
        )


class HandleFormView(SingleObjectMixin, FormView):
    pk_url_kwarg = 'node_pk'
    model = Node

    def get(self, request, node_pk):
        # This will raise a KeyError when `from` is for some reason
        # missing. What should it actually do?
        return redirect(request.GET['from'])

    def get_form_class(self):
        self.form_node = self.get_object()
        self.root_node = self.form_node.get_root()

        # not really necessary to prefetch two trees here, but if we just
        # prefetched root_node we would have to find a prefetched instance of
        # form_node in its tree.
        Node.prefetch_trees(self.form_node, self.root_node)

        return self.form_node.content.build_form_class()

    def form_valid(self, form):
        return self.form_node.content.execute(self.request, form)

    def get_page(self):
        return get_page_from_node(self.root_node)

    def form_invalid(self, form):
        page = self.get_page()

        return page_view(self.request, page.slug, extra_context={
            'page': page,
            'root_node_override': self.root_node,
            self.form_node.content.context_var: form,
        })

handle_form = HandleFormView.as_view()


def preview(request, node_pk, node=None):
    node = node or get_object_or_404(Node, pk=node_pk)

    page = get_page_from_node(node)

    context = {
        'page': page,
        'root_node_override': node,
        '_current_page': page,
    }

    return page_view(request, page.slug, extra_context=context)
