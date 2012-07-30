from widgy.models import *


page = ContentPage.objects.create(
        title='widgy page'
        )
page.root_node = TwoColumnLayout.add_root().node
page.save()

for i in range(3):
    page.root_node.content.left_bucket.content.add_child(TextContent,
            content='yay %s' % i
            )

for i in range(2):
    page.root_node.content.right_bucket.content.add_child(TextContent,
            content='yay right bucket %s' % i
            )
