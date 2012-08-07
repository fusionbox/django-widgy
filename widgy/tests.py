from django.test import TestCase

from widgy.models import ContentPage, TwoColumnLayout, Bucket, TextContent


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


class TreeFetchingOptimization(TestCase):
    def setUp(self):
        page = ContentPage.objects.create(
                title='test page'
                )
        page.root_node = TwoColumnLayout.add_root().node
        page.save()

        for i in range(7):
            page.root_node.content.left_bucket.content.add_child(TextContent,
                    content='yay %s' % i
                    )
        for i in range(5):
            page.root_node.content.right_bucket.content.add_child(TextContent,
                    content='yay right bucket %s' % i
                    )

        self.page = page

    def test_layout_bucket_creation(self):
        """
        Ensures that the manual tree building is accurately building the
        same tree in the same ordes that the mp_tree api would build
        """
        page = self.page

        root = page.root_node

        def test_children(parent):
            if not hasattr(self, '_children'):
                parent.prefetch_tree()
            built_children = parent._children
            del parent._children
            self.assertTrue(built_children == list(parent.get_children()))

        test_children(root)
        for descendant in root.get_descendants():
            test_children(descendant)
