from itertools import izip_longest

from django.test import TestCase

from widgy.utils import html_to_plaintext

class HtmlToText(TestCase):

    def assertContainsSameWords(self, string1, string2):
        try:
            for w1, w2 in izip_longest(string1.split(), string2.split(), fillvalue=''):
                self.assertEqual(w1, w2)
        except AssertionError:
            raise AssertionError("%r does not contain the same words as %r" % (string1,
                                                                               string2))

    def test_basic_conversion(self):

        self.assertContainsSameWords(
            html_to_plaintext("<p>content</p>"),
            'content'
        )

        self.assertContainsSameWords(
            html_to_plaintext("<p>content with multiple words</p>"),
            'content with multiple words'
        )

        self.assertContainsSameWords(
            html_to_plaintext("<p>multiple</p><p>content</p>"),
            'multiple content'
        )

        self.assertContainsSameWords(
            html_to_plaintext(
                '''<div><p>complex</p><p>content</p></div>
                <p>with <a href="#">encapsulation</a></p>'''
            ),
            'complex content with encapsulation'
        )

    def test_comments(self):

        self.assertContainsSameWords(
            html_to_plaintext("<!-- comment --><p>content</p>"),
            'content'
        )

        self.assertContainsSameWords(
            html_to_plaintext("<p>content<!-- comment --></p>"),
            'content',
        )

    def test_non_text(self):
        self.assertContainsSameWords(
            html_to_plaintext("<script>javascript</script><p>content</p>"),
            'content'
        )

        self.assertContainsSameWords(
            html_to_plaintext("<style>css</style><p>content<p>"),
            'content'
        )

        self.assertContainsSameWords(
            html_to_plaintext("<script>javascript<p>javascript</p></script><p>content</p>"),
            'content'
        )

    def test_title_attribute(self):
        self.assertContainsSameWords(
            html_to_plaintext('<p title="title">content</p>'),
            'title content'
        )

        self.assertContainsSameWords(
            html_to_plaintext('<p title="title">content</p><p title="title2">content2</p>'),
            'title content title2 content2'
        )
