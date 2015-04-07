from __future__ import absolute_import
import copy

from django import forms
from django.test import TestCase

from widgy.models.links import (
    link_registry, get_link_field_from_model, LinkFormMixin, LinkFormField,
    get_composite_key, convert_linkable_to_choice, LinkRegistry, LinkField
)

from ..models import (
    LinkableThing, ThingWithLink, AnotherLinkableThing, LinkableThing3,
    Bucket, VersionPageThrough, ChildThingWithLink
)


class TestLinkField(TestCase):
    def test_inheritance(self):
        # the only field local to ChildThingWithLink is its pk. The link
        # field is inherited, so it shouldn't be in local_fields.
        self.assertFalse(any(
            i.name == 'linkable_content_type' for i in ChildThingWithLink._meta.local_fields
        ))

    def test_copy(self):
        # a LinkField has a reference to a LinkRegistry. Copying the LinkField
        # shouldn't copy the registry. Copying the field happens with model
        # inheritance.
        registry = LinkRegistry()
        f1 = LinkField(link_registry=registry)
        f2 = copy.deepcopy(f1)
        self.assertIs(f1._link_registry, f2._link_registry)


class TestLinkRelations(TestCase):
    def test_get_all_linkable_classes(self):
        self.assertIn(LinkableThing, link_registry)
        self.assertIn(AnotherLinkableThing, link_registry)

    def test_get_all_linker_classes(self):
        self.assertIn(ThingWithLink, link_registry.get_all_linker_classes())
        self.assertNotIn(Bucket, link_registry.get_all_linker_classes())
        self.assertNotIn(VersionPageThrough, link_registry.get_all_linker_classes())

    def test_get_all_links_for_obj(self):
        linkable = LinkableThing.objects.create()

        self.assertEqual(len(list(link_registry.get_links(linkable))), 0)

        thing = ThingWithLink.objects.create(
            link=linkable,
        )

        self.assertEqual(list(link_registry.get_links(linkable)), [thing])

        linkable2 = AnotherLinkableThing.objects.create()

        thing2 = ThingWithLink.objects.create(
            link=linkable2,
        )

        self.assertEqual(list(link_registry.get_links(linkable2)), [thing2])

    def test_get_all_possible_linkables(self):
        l1 = LinkableThing.objects.create()
        l2 = LinkableThing.objects.create()
        l3 = AnotherLinkableThing.objects.create()

        choices = get_link_field_from_model(ThingWithLink, 'link').get_choices()

        keyfn = get_composite_key
        self.assertEqual(sorted(list(choices), key=keyfn), sorted([l3, l1, l2], key=keyfn))


class LinkForm(LinkFormMixin, forms.ModelForm):
    link = LinkFormField()

    class Meta:
        model = ThingWithLink
        fields = ('link',)


class TestLinkForm(TestCase):
    def test_save_and_create(self):
        page = LinkableThing.objects.create()
        form = LinkForm()
        choice = get_composite_key(page)
        form = LinkForm({
            'link': choice,
        })
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.link, page)

        form2 = LinkForm({
            'link': choice,
        })
        # save without validating.
        form2.save(commit=False)

    def test_choices(self):
        page1 = LinkableThing.objects.create(name='Z')
        page2 = LinkableThing.objects.create(name='a')
        page3 = AnotherLinkableThing.objects.create()
        page4 = LinkableThing3.objects.create()
        form = LinkForm()

        self.assertEqual(form.fields['link'].choices, [
            ('Another linkable things', [
                convert_linkable_to_choice(page3),
            ]),
            ('Linkable things', [
                convert_linkable_to_choice(page2),
                convert_linkable_to_choice(page1),
            ]),
            ('ZZZZZ should be last', [
                convert_linkable_to_choice(page4),
            ]),
        ])
