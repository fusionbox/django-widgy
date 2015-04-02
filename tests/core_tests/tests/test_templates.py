from __future__ import absolute_import
import uuid

from django.test import TestCase
from django.template import Template, Context

from widgy.models import VersionTracker

from ..widgy_config import widgy_site
from ..models import (
    RawTextWidget, HasAWidgy, VersionedPage,
    MyInvisibleBucket, WeirdPkBucket
)

from widgy.templatetags.widgy_tags import mdown
from widgy.utils import unique_everseen


TEMPLATE = """
{% load widgy_tags %}
{% render_root owner field_name %}
"""


class TestTemplate(TestCase):
    string_to_look_for = uuid.uuid4().hex

    def render(self, context):
        t = Template(TEMPLATE)
        c = Context(context)
        return t.render(c)

    def plain_model(self):
        node = RawTextWidget.add_root(widgy_site,
                                      text=self.string_to_look_for).node
        return HasAWidgy.objects.create(
            widgy=node,
        )

    def test_render_node(self):
        owner = self.plain_model()
        self.assertIn(self.string_to_look_for,
                      self.render({'owner': owner, 'field_name': 'widgy'}))

    def test_root_node_override(self):
        owner = self.plain_model()

        override_string = uuid.uuid4().hex
        override = RawTextWidget.add_root(widgy_site, text=override_string).node

        rendered = self.render({'owner': owner, 'field_name': 'widgy', 'root_node_override': override})

        self.assertNotIn(self.string_to_look_for, rendered)
        self.assertIn(override_string, rendered)

    def versioned_model(self):
        node = RawTextWidget.add_root(widgy_site,
                                      text=self.string_to_look_for).node
        vt = VersionTracker.objects.create(working_copy=node)
        vt.commit()

        return VersionedPage.objects.create(
            version_tracker=vt
        )

    def test_render_versiontracker(self):
        owner = self.versioned_model()
        self.assertIn(self.string_to_look_for,
                      self.render({'owner': owner, 'field_name': 'version_tracker'}))

    def test_versioned_override(self):
        owner = self.versioned_model()

        override_string = uuid.uuid4().hex
        override = RawTextWidget.add_root(widgy_site, text=override_string).node

        rendered = self.render({'owner': owner, 'field_name': 'version_tracker', 'root_node_override': override})

        self.assertNotIn(self.string_to_look_for, rendered)
        self.assertIn(override_string, rendered)


class TestMarkdownXss(TestCase):
    def test_it(self):
        test_cases = [
            ('<script>1', '<script'),
            ('<a onclick="a">asdf</a>', '<a'),
            ("<img SRC=JaVaScRiPt:alert('XSS')>", '<img'),
            ('<div style="background: url("asdf");"></div>', '<div'),
            ('<a href="javascript:foo"></a>', '<a'),
            ('<link rel=stylesheet href=http://asdf>', '<link'),
            ('<meta HTTP-EQUIV="refresh" CONTENT="0;url=javascript:alert(1);">', '<meta'),
            ('<table BACKGROUND="javascript:alert(1)">', '<table'),
            (r"<div style=\"background-image:\0075\0072\006C\0028'\006a\0061\0076\0061\0073\0063\0072\0069\0070\0074\003a\0061\006c\0065\0072\0074\0028.1027\0058.1053\0053\0027\0029'\0029\"></div>", '<div'),
            ('<p style="margin-left: expression(alert(1))">foo</p>', '<p style'),
            ('<HEAD><META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=UTF-7"> </HEAD>+ADw-SCRIPT+AD4-alert(1);+ADw-/SCRIPT+AD4-', '<meta'),
            ('<style>foo</style>', '<style'),
            ('<p style="-moz-binding: url("http://example.com")">asdf</p>', '<p style'),
            ('<!--<script></script>-->', '<script>'),
            ('<img """><script>alert("xss")</script>">', '<script'),
            ('<img src= onmouseover="alert(1)">', ' <img'),
            ('<html xmlns:xss><?import namespace="xss" implementation="http://ha.ckers.org/xss.htc"><xss:xss>ss</xss:xss></html>',
             '<?import'),
            ('<!--[if gte IE 4]><script>alert(1);</script><![endif]-->', '<script>'),
            ('{@onclick=alert(1)}paragraph', '<p onclick'),
        ]

        for html, must_not_occur in test_cases:
            cleaned = mdown(html)
            self.assertNotIn(must_not_occur, cleaned)


class TestTemplateHierarchy(TestCase):
    def test_hierarchy_involving_non_model_mixins(self):
        self.assertEqual(list(unique_everseen(MyInvisibleBucket.get_templates_hierarchy(template_name='test'))), [
            'widgy/core_tests/myinvisiblebucket/test.html',
            'widgy/mixins/invisible/test.html',
            'widgy/widgy/content/test.html',
            'widgy/core_tests/test.html',
            'widgy/mixins/test.html',
            'widgy/widgy/test.html',
            'widgy/test.html',
        ])

    def test_hierarchy_with_inheritance(self):
        self.assertEqual(list(unique_everseen(WeirdPkBucket.get_templates_hierarchy(template_name='test'))), [
            'widgy/core_tests/weirdpkbucket/test.html',
            'widgy/core_tests/weirdpkbucketbase/test.html',
            'widgy/core_tests/weirdpkbase/test.html',
            'widgy/widgy/content/test.html',
            'widgy/core_tests/test.html',
            'widgy/widgy/test.html',
            'widgy/test.html',
        ])
