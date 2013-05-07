from django.core import urlresolvers

from widgy.models.links import LinkableMixin


class WidgyPageMixin(LinkableMixin):
    def get_form_action_url(self, form, widgy):
        return urlresolvers.reverse(
            'widgy.contrib.widgy_mezzanine.views.handle_form',
            kwargs={
                'form_node_pk': form.node.pk,
                'root_node_pk': widgy['root_node'].pk,
            })
