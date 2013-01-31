from django.test import TestCase
from django import forms
from django.contrib.contenttypes.models import ContentType

from widgy.forms import WidgyFormMixin, WidgyFormField
from widgy.models import Node

from modeltests.core_tests.widgy_config import widgy_site
from modeltests.core_tests.models import (HasAWidgy, Layout, HasAWidgyOnlyAnotherLayout, AnotherLayout)


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

        the_layout_contenttype = ContentType.objects.get_for_model(AnotherLayout)
        x = TheForm({'widgy': the_layout_contenttype.id})
        layout_contenttypes = x.fields['widgy'].queryset.all()
        self.assertEqual(len(layout_contenttypes), 1)
        self.assertIn(the_layout_contenttype, layout_contenttypes)


class WidgiedForm(WidgyFormMixin, forms.Form):
    text_field = forms.CharField()
    widgy_field = WidgyFormField(
        queryset=ContentType.objects.filter(model__in=['layout', 'anotherlayout']),
        site=widgy_site,
    )

class TestPlainForm(TestCase):
    def test_render_initial(self):
        x = WidgiedForm()
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
        x = WidgiedForm({
            'text_field': 'foo',
            'widgy_field': str(ContentType.objects.get_for_model(AnotherLayout).id),
        })
        self.assertTrue(x.is_valid())

        x = WidgiedForm({
            'text_field': 'foo',
            'widgy_field': str(ContentType.objects.get_for_model(HasAWidgy).id),
        })
        self.assertFalse(x.is_valid())

    def test_second_save(self):
        # todo...I don't even know what the api for a non-modelform widgy field is
        root_node = Layout.add_root(widgy_site)
        x = WidgiedForm(initial={'widgy_field': root_node})


class WidgiedModelForm(WidgyFormMixin, forms.ModelForm):
    text_field = forms.CharField()

    class Meta:
        model = HasAWidgy

class TestModelForm(TestCase):
    def test_render_initial(self):
        x = WidgiedModelForm()
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
        x = WidgiedModelForm({
            'text_field': 'asdf',
            'widgy': ContentType.objects.get_for_model(AnotherLayout).id,
        })
        self.assertTrue(x.is_valid())
        instance = x.save()
        self.assertIsInstance(instance.widgy, Node)
        self.assertIsInstance(instance.widgy.content, AnotherLayout)

    def test_initial_save_invalid(self):
        x = WidgiedModelForm({
            'text_field': 'asdf',
            'widgy': ContentType.objects.get_for_model(HasAWidgy).id,
        })
        self.assertFalse(x.is_valid())

    def test_second_render(self):
        from fusionbox.core.templatetags.fusionbox_tags import json as json_tag
        instance = HasAWidgy.objects.create(
            widgy=Layout.add_root(widgy_site).node
        )
        x = WidgiedModelForm(instance=instance)
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
        x = WidgiedModelForm(instance=instance, data={
            'widgy': '1',
            'text_field': 'asdf',
        })

        # what assertions can we do here?
        x.save()

    def test_single_content_type(self):
        class Form(WidgyFormMixin, forms.ModelForm):
            class Meta:
                model = HasAWidgyOnlyAnotherLayout

        x = Form()
        self.assertIn(AnotherLayout._meta.verbose_name.lower(),
                      x.as_p().lower())

        x = Form({})
        self.assertTrue(x.is_valid())
        instance = x.save()
        self.assertIsInstance(instance.widgy.content, AnotherLayout)
