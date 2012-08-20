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
        root.prefetch_tree()

        def test_children(parent):
            children = parent._children
            del parent._children
            self.assertTrue(children == list(parent.get_children()))
            parent._children = children

        descendents = [root]
        while descendents:
            descendent = descendents.pop()
            descendents += descendent.get_children()
            test_children(descendent)



from django.contrib.auth.models import User
import json
from pprint import pprint

from widgy.models import TwoColumnLayout, Node
from widgy.views import extract_id

class HttpTestCase(TestCase):
    def setUp(self):
        u = User.objects.create_user(
                username='testuser',
                email='asdf@example.com',
                password='asdfasdf',
                )
        u.is_superuser = True
        u.save()
        self.client.login(username=u.username, password='asdfasdf')
        self.user = u

    def json_request(self, method, url, data=None):
        method = getattr(self.client, method)
        if method == self.client.get:
            encode = lambda x: x
        else:
            encode = json.dumps
        if data:
            resp = method(url, encode(data), content_type='application/json')
        else:
            resp = method(url, content_type='application/json')

        assert resp['Content-Type'] == 'application/json'

        return resp

    def __getattr__(self, attr):
        if attr in ('get', 'post', 'put', 'delete', 'trace', 'head', 'patch'):
            return lambda *args, **kwargs: self.json_request(attr, *args, **kwargs)
        else:
            return super(HttpTestCase, self).__getattr__(attr)

class TestApi(HttpTestCase):
    def setUp(self):
        super(TestApi, self).setUp()

        # widgy always has a root node
        self.root_node = TwoColumnLayout.add_root().node
        self.node_url = '/admin/widgy/node/'

    def test_textcontent_available(self):
        available_children = json.loads(self.get(self.root_node.to_json()['available_children_url']).content)
        assert 'widgy.textcontent' in [i['__class__'] for i in available_children]

    def test_add_child(self):
        bucket = self.root_node.to_json()['children'][0]
        db_bucket = Node.objects.get(id=extract_id(bucket['url']))
        assert db_bucket.get_children_count() == 0

        new_child = self.post(self.node_url, {
            '__class__': 'widgy.textcontent',
            'parent_id': bucket['url'],
            'right_id': None,
            })
        assert new_child.status_code == 201
        new_child = json.loads(new_child.content)
        assert new_child['parent_id'] == bucket['url']
        assert new_child['content']['__class__'] == 'widgy.textcontent'

        db_bucket = Node.objects.get(id=extract_id(bucket['url']))
        assert db_bucket.get_children_count() == 1


        new_child['content']['content'] = 'foobar'
        r = self.put(new_child['content']['url'], new_child['content'])
        assert r.status_code == 200

        r = self.get(new_child['content']['url'])
        assert r.status_code == 200
        textcontent = json.loads(r.content)
        assert textcontent['content'] == 'foobar'

        # move the node to the other bucket

        new_child['parent_id'] = self.root_node.to_json()['children'][1]['url']
        r = self.put(new_child['url'], new_child)
        assert r.status_code == 200
        r = json.loads(r.content)

        assert r['parent_id'] == self.root_node.to_json()['children'][1]['url']
