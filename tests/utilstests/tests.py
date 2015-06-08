from six.moves import zip_longest

from django.test import TestCase
from django.db import models

from widgy.utils import html_to_plaintext, unset_pks, model_has_field

from .models import Child


class HtmlToText(TestCase):

    def assertContainsSameWords(self, string1, string2):
        try:
            for w1, w2 in zip_longest(string1.split(), string2.split(), fillvalue=''):
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

    def test_alt_attribute(self):
        self.assertContainsSameWords(
            html_to_plaintext('<img alt="image description" />'),
            'image description'
        )

        self.assertContainsSameWords(
            html_to_plaintext('<p>content</p><img alt="image description" />'),
            'content image description'
        )

    def test_other_attributes(self):
        self.assertContainsSameWords(
            html_to_plaintext('<a href="http://example.com">example.com</a>'),
            'example.com'
        )

        self.assertContainsSameWords(
            html_to_plaintext('<body onload="javascript:alert(\'hello\')">content</body>'),
            'content'
        )

        self.assertContainsSameWords(
            html_to_plaintext('<span lang="en" onclick="javascript:void(0)">content</span>'),
            'content'
        )


class TestUnsetPks(TestCase):
    def test_unset_pks(self):
        obj = Child.objects.create()
        unset_pks(obj)
        self.assertIsNone(obj.foo)
        self.assertIsNone(obj.base_ptr_id)


class FieldExistsModel(models.Model):
    field_a = models.IntegerField()


class ChildFieldExistsModel(FieldExistsModel):
    field_b = models.IntegerField()


class TestLinkField(TestCase):
    def test_for_existing_field(self):
        assert model_has_field(FieldExistsModel, 'field_a')

    def test_for_non_existent_field(self):
        assert not model_has_field(FieldExistsModel, 'does_not_exist')

    def test_for_existing_field_on_child_model(self):
        assert model_has_field(ChildFieldExistsModel, 'field_a')
        assert model_has_field(ChildFieldExistsModel, 'field_b')

    def test_for_non_existent_field_on_child_model(self):
        assert not model_has_field(ChildFieldExistsModel, 'does_not_exist')
        assert not model_has_field(ChildFieldExistsModel, 'does_not_exist')
