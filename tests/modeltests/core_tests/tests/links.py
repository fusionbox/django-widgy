from django import forms
from django.test import TestCase

from widgy.models.links import (
    get_all_linkable_classes, get_all_linker_classes,
    get_link_field_from_model, LinkFormMixin, LinkFormField,
    get_composite_key, convert_linkable_to_choice,
)

from modeltests.core_tests.models import (
    LinkableThing, ThingWithLink, AnotherLinkableThing,
    Bucket, VersionPageThrough
)


class TestLinkRelations(TestCase):
    def test_get_all_linkable_classes(self):
        self.assertIn(LinkableThing, get_all_linkable_classes())
        self.assertIn(AnotherLinkableThing, get_all_linkable_classes())

    def test_get_all_linker_classes(self):
        self.assertIn(ThingWithLink, get_all_linker_classes())
        self.assertNotIn(Bucket, get_all_linker_classes())
        self.assertNotIn(VersionPageThrough, get_all_linker_classes())

    def test_get_all_links_for_obj(self):
        linkable = LinkableThing.objects.create()

        self.assertEqual(len(list(linkable.get_links())), 0)

        thing = ThingWithLink.objects.create(
            link=linkable,
        )

        self.assertEqual(list(linkable.get_links()), [thing])

        linkable2 = AnotherLinkableThing.objects.create()

        thing2 = ThingWithLink.objects.create(
            link=linkable2,
        )

        self.assertEqual(list(linkable2.get_links()), [thing2])

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
        form = LinkForm()

        # TODO: this has an implicit ordering check, that might be brittle.
        self.assertEqual(form.fields['link'].choices, [
            (LinkableThing._meta.verbose_name_plural, [
                convert_linkable_to_choice(page2),
                convert_linkable_to_choice(page1),
            ]),
            (AnotherLinkableThing._meta.verbose_name_plural, [
                convert_linkable_to_choice(page3),
            ]),
        ])
