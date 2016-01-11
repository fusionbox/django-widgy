from django.views.generic.edit import FormMixin
from django.shortcuts import get_object_or_404
from widgy.models import Node


class HandleFormMixin(FormMixin):
    """
    An abstract view mixin for handling form_builder.Form submissions.
    """
    def post(self, *args, **kwargs):
        """
        copied from django.views.generic.edit.ProcessFormView, because we want
        the post method, but not the get method.
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    put = post

    def get_form_node(self):
        node = get_object_or_404(Node, pk=self.kwargs['form_node_pk'])
        node.prefetch_tree()
        return node

    def get_form_class(self):
        self.form_node = self.get_form_node()
        return self.form_node.content.build_form_class()

    def get_form(self, form_class=None):
        # Django now calls get_form in get_context_data, but HandleFormMixin
        # needs to still work even if no form exists.
        if form_class is None:
            if self.kwargs.get('form_node_pk') is None:
                return None
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        if 'form' in kwargs:
            kwargs.setdefault(self.form_node.content.context_var, kwargs['form'])
        return super(HandleFormMixin, self).get_context_data(**kwargs)

    def form_valid(self, form):
        return self.form_node.content.execute(self.request, form)
