import uuid

from django.test import TestCase
from django.test.client import RequestFactory
from django.template import Template, Context

from widgy.models import VersionTracker

from modeltests.core_tests.widgy_config import widgy_site
from modeltests.core_tests.models import RawTextWidget

TEMPLATE = """
{% load widgy_tags %}
{% render node %}
"""

class TestTemplate(TestCase):
    string_to_look_for = uuid.uuid4().hex

    def render(self, context):
        defaults = {
            'request': RequestFactory().get('/'),
        }
        defaults.update(context)
        t = Template(TEMPLATE)
        c = Context(defaults)
        return t.render(c)

    def test_render_node(self):
        node = RawTextWidget.add_root(widgy_site,
                                      text=self.string_to_look_for).node
        self.assertIn(self.string_to_look_for,
                      self.render({'node': node}))

    def test_render_content(self):
        content = RawTextWidget.add_root(widgy_site,
                                      text=self.string_to_look_for)
        self.assertIn(self.string_to_look_for,
                      self.render({'node': content}))

    def test_render_versiontracker(self):
        node = RawTextWidget.add_root(widgy_site,
                                      text=self.string_to_look_for).node
        vt = VersionTracker.objects.create(working_copy=node)
        vt.commit()

        self.assertIn(self.string_to_look_for,
                      self.render({'node': vt}))
