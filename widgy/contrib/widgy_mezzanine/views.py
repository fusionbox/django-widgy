# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q

from mezzanine.pages.models import Page
from mezzanine.pages.views import page as page_view

from widgy.contrib.widgy_mezzanine.models import WidgyPage
from widgy.models import Node


def handle_form(request, node_pk):
    form_node = get_object_or_404(Node, pk=node_pk)
    page = get_object_or_404(Page, pk=request.GET['page_pk'])

    form_class = form_node.content.get_form()

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            resp = form_node.content.execute(request, form)
            return resp or redirect(page.get_absolute_url())
        return page_view(request, page.slug, extra_context={
            'page': page,
            form_node.content.context_var: form,
        })
    else:
        return redirect(page.get_absolute_url())

def preview(request, node_pk, node=None):
    node = node or get_object_or_404(Node, pk=node_pk)

    widgy_page = get_object_or_404(
        WidgyPage.objects.distinct(),
        Q(root_node__commits__root_node=node) | Q(root_node__working_copy=node)
    )
    page = widgy_page.page_ptr

    return page_view(request, page.slug, extra_context={
        'page': page,
        'root_node_override': node,
    })
