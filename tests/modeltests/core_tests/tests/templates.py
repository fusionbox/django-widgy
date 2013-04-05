import uuid

from django.test import TestCase
from django.test.client import RequestFactory
from django.template import Template, Context

from widgy.models import VersionTracker

from modeltests.core_tests.widgy_config import widgy_site
from modeltests.core_tests.models import RawTextWidget

from widgy.templatetags.widgy_tags import mdown

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
