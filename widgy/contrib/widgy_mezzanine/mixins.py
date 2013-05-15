from django.core import urlresolvers

from widgy.models.links import LinkableMixin
from widgy.exceptions import CannotBeCached


class WidgyPageMixin(LinkableMixin):
    base_template = 'widgy/mezzanine_base.html'

    @property
    def seo_keywords(self):
        """
        This is here to prevent a mess in the template, but also because the
        KeywordsField from mezzanine seems to be doing much too much for what
        we need.  We also override this with a real db column in order to do
        translation.
        """
        return ', '.join(unicode(keyword) for keyword in self.keywords.all())

    def get_form_action_url(self, form, widgy):
        return urlresolvers.reverse(
            'widgy.contrib.widgy_mezzanine.views.handle_form',
            kwargs={
                'form_node_pk': form.node.pk,
                'root_node_pk': widgy['root_node'].pk,
            })

    def get_cache_key(self, widgy_env, context):
        request = context.get('request')

        if request and request.method != 'GET':
            raise CannotBeCached

        return ':'.join([
            self.title,
            (request and request.get_full_path()) or self.get_absolute_url()
        ])
