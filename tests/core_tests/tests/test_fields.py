from __future__ import absolute_import
import copy
import unittest

from django.test import TestCase
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.template import Context

import mock

from widgy.forms import WidgyFormMixin, WidgyFormField
from widgy.models import Node, VersionTracker

from ..widgy_config import widgy_site
from ..models import (
    HasAWidgy, HasAWidgyNonNull, Layout, HasAWidgyOnlyAnotherLayout, AnotherLayout,
    VersionedPage, RawTextWidget)


class TestWidgyField(TestCase):
    def test_it_acts_like_a_foreignkey(self):
        x = HasAWidgy()
        x.widgy = Layout.add_root(widgy_site).node
        x.save()

        x = HasAWidgy.objects.get(pk=x.pk)
        self.assertIsInstance(x.widgy.content, Layout)

    def test_formfield(self):
        class TheForm(forms.ModelForm):
            class Meta:
                model = HasAWidgy
                fields = '__all__'

        the_layout_contenttype = ContentType.objects.get_for_model(Layout)
        x = TheForm({'widgy': the_layout_contenttype.id})
        layout_contenttypes = x.fields['widgy'].queryset.all()
        self.assertEqual(len(layout_contenttypes), 2)
        self.assertIn(the_layout_contenttype, layout_contenttypes)
        self.assertIn(ContentType.objects.get_for_model(AnotherLayout),
                      layout_contenttypes)

        self.assertTrue(x.is_valid())
        obj = x.save()
        self.assertIsInstance(obj.widgy.content, Layout)

    def test_sublayout(self):
        class TheForm(forms.ModelForm):
            class Meta:
                model = HasAWidgyOnlyAnotherLayout
                fields = '__all__'

        the_layout_contenttype = ContentType.objects.get_for_model(AnotherLayout)
        x = TheForm({'widgy': the_layout_contenttype.id})
        layout_contenttypes = x.fields['widgy'].queryset.all()
        self.assertEqual(len(layout_contenttypes), 1)
        self.assertIn(the_layout_contenttype, layout_contenttypes)

    def test_add_root(self):
        instance = HasAWidgy()
        instance.widgy = ContentType.objects.get_for_model(Layout)
        root_node = HasAWidgy._meta.get_field('widgy').add_root(instance, {
            'pk': 1337,
        })

        self.assertEqual(root_node.content.pk, 1337)

    def test_override_add_root(self):
        """
        If we put a widgy content before save()ing, the root_node shouldn't be overridden.
        """
        instance = HasAWidgy()

        field = HasAWidgy._meta.get_field('widgy')
        instance.widgy = ContentType.objects.get_for_model(Layout)
        instance.widgy = field.add_root(instance, {'pk': 1337})
        instance.save()

        self.assertEqual(instance.widgy.content.pk, 1337)


@unittest.skip("We want WidgyFields to work with non-modelforms, but we haven't designed an API yet.")
class TestPlainForm(TestCase):
    def setUp(self):
        # WidgyForms cannot be at the root level of a test because they make
        # database calls and the database isn't setup yet.
        class WidgiedForm(WidgyFormMixin, forms.Form):
            text_field = forms.CharField()
            widgy_field = WidgyFormField(
                queryset=ContentType.objects.filter(model__in=['layout', 'anotherlayout']),
                site=widgy_site,
            )

        self.form = WidgiedForm

    def test_render_initial(self):
        x = self.form()
        rendered = x.as_p()
        self.assertIn('value="%s"' % ContentType.objects.get_for_model(Layout).id,
                      rendered)
        self.assertIn('value="%s"' % ContentType.objects.get_for_model(AnotherLayout).id,
                      rendered)
        self.assertIn('name="widgy_field"',
                      rendered)
        self.assertIn('name="text_field"',
                      rendered)
        # class names
        self.assertIn('core_tests',
                      rendered)
        self.assertIn('anotherlayout',
                      rendered)

    def test_initial_save(self):
        x = self.form({
            'text_field': 'foo',
            'widgy_field': str(ContentType.objects.get_for_model(AnotherLayout).id),
        })
        self.assertTrue(x.is_valid())

        x = self.form({
            'text_field': 'foo',
            'widgy_field': str(ContentType.objects.get_for_model(HasAWidgy).id),
        })
        self.assertFalse(x.is_valid())

    def test_second_save(self):
        # todo...I don't even know what the api for a non-modelform widgy field is
        root_node = Layout.add_root(widgy_site)
        x = self.form(initial={'widgy_field': root_node})


class TestModelForm(TestCase):
    def setUp(self):
        class WidgiedModelForm(WidgyFormMixin, forms.ModelForm):
            text_field = forms.CharField()

            class Meta:
                model = HasAWidgy
                fields = '__all__'

        self.form = WidgiedModelForm

    def test_render_initial(self):
        x = self.form()
        rendered = x.as_p()
        self.assertIn('value="%s"' % ContentType.objects.get_for_model(Layout).id,
                      rendered)
        self.assertIn('value="%s"' % ContentType.objects.get_for_model(AnotherLayout).id,
                      rendered)
        self.assertIn('name="widgy"',
                      rendered)
        self.assertIn('name="text_field"',
                      rendered)
        # class names
        self.assertIn('core_tests',
                      rendered)
        self.assertIn('anotherlayout',
                      rendered)

    def test_initial_save(self):
        x = self.form({
            'text_field': 'asdf',
            'widgy': ContentType.objects.get_for_model(AnotherLayout).id,
        })
        self.assertTrue(x.is_valid())
        instance = x.save()
        self.assertIsInstance(instance.widgy, Node)
        self.assertIsInstance(instance.widgy.content, AnotherLayout)

    def test_initial_save_invalid(self):
        x = self.form({
            'text_field': 'asdf',
            'widgy': ContentType.objects.get_for_model(HasAWidgy).id,
        })
        self.assertFalse(x.is_valid())

    def test_second_render(self):
        from argonauts.templatetags.argonauts import json as json_tag
        instance = HasAWidgy.objects.create(
            widgy=Layout.add_root(widgy_site).node
        )
        x = self.form(instance=instance)
        rendered = x.as_p()

        self.assertIn('input type="hidden" name="widgy" value="%s"' % instance.widgy.pk,
                      rendered)
        self.assertIn('new Widgy',
                      rendered)
        self.assertIn(json_tag(instance.widgy.to_json(widgy_site)),
                      rendered)

    def test_second_save(self):
        instance = HasAWidgy.objects.create(
            widgy=Layout.add_root(widgy_site).node
        )
        x = self.form(instance=instance, data={
            'widgy': '1',
            'text_field': 'asdf',
        })

        # what assertions can we do here?
        x.save()

    def test_single_content_type(self):
        class Form(WidgyFormMixin, forms.ModelForm):
            class Meta:
                model = HasAWidgyOnlyAnotherLayout
                fields = '__all__'

        x = Form()
        self.assertIn(AnotherLayout._meta.verbose_name.lower(),
                      x.as_p().lower())

        x = Form({})
        self.assertTrue(x.is_valid())
        instance = x.save()
        self.assertIsInstance(instance.widgy.content, AnotherLayout)

    def test_formfield_non_null(self):
        class TheForm(WidgyFormMixin, forms.ModelForm):
            class Meta:
                model = HasAWidgyNonNull
                fields = '__all__'

        x = TheForm({})
        self.assertTrue(x.is_valid())
        obj = x.save()
        self.assertTrue(obj.widgy)


class TestVersionedModelForm(TestCase):
    def setUp(self):
        class VersionedWidgiedForm(WidgyFormMixin, forms.ModelForm):
            class Meta:
                model = VersionedPage
                fields = '__all__'
        self.form = VersionedWidgiedForm

    def test_render(self):
        x = self.form()
        rendered = x.as_p()
        self.assertIn('value="%s"' % ContentType.objects.get_for_model(Layout).id,
                      rendered)
        self.assertIn('value="%s"' % ContentType.objects.get_for_model(AnotherLayout).id,
                      rendered)
        self.assertIn('name="version_tracker"',
                      rendered)
        self.assertIn('core_tests',
                      rendered)
        self.assertIn('anotherlayout',
                      rendered)

    def test_first_save_noroot(self):
        x = self.form({})

        self.assertTrue(x.is_valid())
        instance = x.save()
        self.assertEqual(instance.version_tracker, None)

    def test_first_save(self):
        x = self.form({
            'version_tracker': ContentType.objects.get_for_model(Layout).id,
        })

        self.assertTrue(x.is_valid())
        instance = x.save()
        self.assertIsInstance(instance.version_tracker, VersionTracker)
        self.assertIsInstance(instance.version_tracker.working_copy.content, Layout)

    def test_second_render(self):
        x = self.form({
            'version_tracker': ContentType.objects.get_for_model(Layout).id,
        })
        instance = x.save()
        x = self.form(instance=instance)
        url = widgy_site.reverse(widgy_site.commit_view, kwargs={'pk': instance.version_tracker.pk})
        self.assertIn(url, x.as_p())


def copy_call_args(mock):
    """
    `copy.copy`s a mock's call_args to handle mutable arguments.

    Like template Context
    """
    new_mock = mock.Mock()
    def side_effect(*args, **kwargs):
        new_args = tuple(copy.copy(i) for i in args)
        new_kwargs = dict((k, copy.copy(v)) for k, v in kwargs.items())
        new_mock(*new_args, **new_kwargs)
        return mock.DEFAULT
    mock.side_effect = side_effect
    return new_mock


class TestRender(TestCase):
    def setUp(self):
        self.widgied = HasAWidgy()
        self.widgied.widgy = Layout.add_root(widgy_site).node
        self.widgied.save()
        self.widgied.widgy.get_children()[1].content.add_child(widgy_site, RawTextWidget, text='asdf')

        self.widgy_field = HasAWidgy._meta.get_field('widgy')

    def test_simple(self):
        rendered = self.widgy_field.render(self.widgied)
        self.assertIn('asdf', rendered)

    def test_widgy_env(self):
        with mock.patch.object(Layout, 'render') as patched_render:
            patched_render = copy_call_args(patched_render)
            self.widgy_field.render(self.widgied)

        args, kwargs = patched_render.call_args
        context = args[0]
        widgy = context['widgy']
        self.assertEqual(widgy['site'], widgy_site)
        self.assertEqual(widgy['owner'], self.widgied)

    def test_parent(self):
        parent_widgy = object()
        context = Context({'widgy': parent_widgy})
        with mock.patch.object(Layout, 'render') as patched_render:
            patched_render = copy_call_args(patched_render)
            self.widgy_field.render(self.widgied, context)

        args, kwargs = patched_render.call_args
        context = args[0]
        widgy = context['widgy']
        self.assertIs(widgy['parent'], parent_widgy)

    def test_null(self):
        """
        Rendering a NULL WidgyField
        """
        self.widgied.widgy = None
        self.widgied.save()
        # doesn't matter what happens as long as it doesn't throw an exception
        self.widgy_field.render(self.widgied)

    def test_null_versioned(self):
        """
        Rendering a NULL VersionedWidgyField
        """
        page = VersionedPage.objects.create()
        field = VersionedPage._meta.get_field('version_tracker')
        # doesn't matter what happens as long as it doesn't throw an exception
        field.render(page)

    def test_no_commits(self):
        """
        Rendering a VersionedWidgyField without any commits
        """
        page = VersionedPage.objects.create(
            version_tracker=VersionTracker.objects.create(
                working_copy=Layout.add_root(widgy_site).node,
            )
        )
        field = VersionedPage._meta.get_field('version_tracker')
        # doesn't matter what happens as long as it doesn't throw an exception
        field.render(page)
