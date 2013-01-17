# Create your views here.
from django.shortcuts import get_object_or_404, redirect

from mezzanine.pages.models import Page
from mezzanine.pages.views import page as page_view

from widgy.models import Node


def handle_form(request, node_pk):
    form_node = get_object_or_404(Node, pk=node_pk)
    page = get_object_or_404(Page, pk=request.POST['page_pk'])

    form_class = form_node.content.get_form()

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            form_node.content.execute(request, form)
            return redirect(page.get_absolute_url())

    return page_view(request, page.slug, extra_context={
        'page': page,
        form_node.content.context_var: form,
    })
