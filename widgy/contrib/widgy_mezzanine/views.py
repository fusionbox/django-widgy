import warnings

from django.db.models import Q
from django.views.generic import View, UpdateView, DetailView
from django.views.generic.detail import SingleObjectMixin
from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.utils.http import is_safe_url
try:
    from django.contrib.admin.utils import unquote
except ImportError:  # < Django 1.8
    from django.contrib.admin.util import unquote
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied
from django.core import urlresolvers
from django import forms
from django.utils.translation import ugettext as _

from mezzanine.pages.views import page as page_view
from mezzanine.pages.models import Page
from mezzanine.core.models import CONTENT_STATUS_DRAFT

from widgy.contrib.form_builder.views import HandleFormMixin
from widgy.contrib.widgy_mezzanine import get_widgypage_model
from widgy.models import Node
from widgy.views.base import AuthorizedMixin
from widgy.utils import fancy_import, unset_pks

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
            slug='restoring-page',
        )


class PageViewMixin(object):
    def get_page(self):
        try:
            qs = Page.objects.published(for_user=self.request.user)
            if 'slug' in self.kwargs:
                warnings.warn(
                """
Using slug when reversing widgy.contrib.widgy_mezzanine.views.handle_form or
widgy.contrib.widgy_mezzanine.preview is deprecated. You should update your
code to look like this:

    url = urlresolvers.reverse('widgy.contrib.widgy_mezzanine.views.preview', kwargs={
        'node_pk': node.pk,
        'page_pk': page.pk,
    })
""",
                    DeprecationWarning
                )
                return qs.get(slug=self.kwargs['slug'])
            else:
                return qs.get(pk=self.kwargs['page_pk'])
        except (KeyError, Page.DoesNotExist):
            # restoring, use a fake page
            return WidgyPage(
                titles='restoring page',
                content_model='widgypage',
                slug='restoring-page',
            )

    def page_view(self, request, page, context):
        # Before Mezzanine==3.1.2, the page view would check extra_context for
        # the page object, so we would pass it in then, starting with 3.1.2 and
        # the introduction of mezzanine.pages.context_processors.page,
        # Mezzanine expects the PageMiddleware to set page on the request. The
        # context_processor will add the page and _current_page values to the
        # context for us, but we are still passing it in for Mezzanine<=3.1.1.
        if hasattr(page, 'page_ptr'):
            # mezzanine.pages.middleware.PageMiddleware sticks a Page object,
            # not a WidgyPage object, to the request so we also need to get the
            # raw Page object.
            page = page.page_ptr

        request.page = page

        extra_context = {
            'page': page,
            '_current_page': page,
        }
        extra_context.update(context)

        return page_view(request, page.slug, extra_context=extra_context)


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

        context = self.get_context_data(
            form=form,
            root_node_override=root_node,
        )

        return self.page_view(self.request, page, context)

handle_form = HandleFormView.as_view()


class PreviewView(AuthorizedMixin, SingleObjectMixin, PageViewMixin, View):
    model = Node
    pk_url_kwarg = 'node_pk'

    def get(self, request, *args, **kwargs):
        node = self.get_object()
        page = self.get_page()
        if 'slug' in self.kwargs:
            return HttpResponsePermanentRedirect(urlresolvers.reverse(
                preview, kwargs={'page_pk': page.pk, 'node_pk': node.pk}
            ))

        context = {
            'root_node_override': node,
        }

        return self.page_view(request, page, context)

preview = PreviewView.as_view(
    site=fancy_import(settings.WIDGY_MEZZANINE_SITE),
)


class CloneForm(forms.ModelForm):
    class Meta:
        model = WidgyPage
        fields = ['title', 'slug']

    def __init__(self, *args, **kwargs):
        super(CloneForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = _('New title')
        self.fields['slug'].label = _('New URL')


class AdminViewMixin(object):
    def get_object(self):
        obj = get_object_or_404(self.model, pk=unquote(self.args[0]))
        return obj

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            raise PermissionDenied
        return super(AdminViewMixin, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return urlresolvers.reverse('admin:{0}_{1}_change'.format(
            self.object._meta.app_label,
            self.object._meta.model_name), args=(self.object.pk,))


class ClonePageView(AdminViewMixin, UpdateView):
    form_class = CloneForm
    template_name = 'widgy/widgy_mezzanine/widgypage_clone_form.html'
    has_permission = None

    def get_object(self):
        obj = super(ClonePageView, self).get_object()
        self.original_title = obj.title
        return obj

    def get_initial(self):
        initial = super(ClonePageView, self).get_initial()
        initial['slug'] = None
        return initial

    def form_valid(self, form):
        page = form.instance
        unset_pks(page)
        page.root_node = page.root_node.clone()
        page.status = CONTENT_STATUS_DRAFT
        form.save()

        messages.success(
            self.request,
            _("'{old_title}' successfully cloned as '{new_title}'.").format(
                old_title=self.original_title,
                new_title=page.title,
            )
        )
        # We can't do a normal HTTP redirect because the form is in a modal
        # window.
        return render(self.request, 'widgy/widgy_mezzanine/clone_success.html', {
            'success_url': self.get_success_url(),
        })

    def get_context_data(self, **kwargs):
        kwargs = super(ClonePageView, self).get_context_data(**kwargs)
        kwargs['is_popup'] = True
        return kwargs


class UnpublishView(AdminViewMixin, DetailView):
    template_name = 'widgy/widgy_mezzanine/unpublish.html'
    has_change_permission = None

    def dispatch(self, request, *args, **kwargs):
        # BBB django 1.4 sets args/kwargs in dispatch not as_view like later
        # versions
        self.args = args
        self.object = self.get_object()
        return super(UnpublishView, self).dispatch(request, *args, **kwargs)

    def has_permission(self, request):
        return self.has_change_permission(request, self.object)

    def post(self, *args, **kwargs):
        self.object.status = CONTENT_STATUS_DRAFT
        self.object.save()
        messages.success(self.request, "Page unpublished.")
        return HttpResponseRedirect(self.get_success_url())
