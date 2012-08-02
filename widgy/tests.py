from django.test import TestCase

from widgy.models import ContentPage, TwoColumnLayout, Bucket


class TwoColumnLayoutTest(TestCase):
    def setUp(self):
        page = ContentPage.objects.create(
                title='test page'
                )
        page.root_node = TwoColumnLayout.add_root().node
        page.save()
        self.page = page

    def test_layout_bucket_creation(self):
        """
        Tests that buckets ar auto-created correctly on layouts.
        """
        page = self.page

        self.assertTrue(isinstance(page.root_node.get_children()[0].content, Bucket))
        self.assertTrue(isinstance(page.root_node.get_children()[1].content, Bucket))
