import json

from django.test import TestCase
from django.contrib.auth.models import User

from modeltests.core_tests.widgy_config import widgy_site
from modeltests.core_tests.models import Layout, RawTextWidget, Bucket


class RootNodeTestCase(TestCase):
    urls = 'modeltests.core_tests.urls'

    def setUp(self):
        self.root_node = Layout.add_root(widgy_site).node



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

    def json_request(self, method, url, data=None, *args, **kwargs):
        method = getattr(self.client, method)
        if method == self.client.get:
            encode = lambda x: x
        else:
            encode = json.dumps
        if data:
            resp = method(url, encode(data), content_type='application/json', *args, **kwargs)
        else:
            resp = method(url, content_type='application/json', *args, **kwargs)

        self.assertEqual(resp['Content-Type'], 'application/json')

        return resp

    def __getattr__(self, attr):
        if attr in ('get', 'post', 'put', 'delete', 'trace', 'head', 'patch'):
            return lambda *args, **kwargs: self.json_request(attr, *args, **kwargs)
        else:
            return getattr(super(HttpTestCase, self), attr)


def tree_to_dot(node):
    output = []
    output.append('digraph {')
    for i in node.depth_first_order():
        output.append('  %s [label="%s: %s"];' % (i.id, i.id, repr(i.content)))
        if i != node:
            output.append('  %s -> %s;' % (i.get_parent().id, i.id))
    output.append('}')
    return '\n'.join(output)


def display_node(node):
    import subprocess
    proc = subprocess.Popen(['dot', '-Tx11'], stdin=subprocess.PIPE)
    proc.communicate(tree_to_dot(node))


def make_a_nice_tree(root_node):
    left, right = root_node.content.get_children()
    left.add_child(widgy_site,
                   RawTextWidget,
                   text='left_1')
    left.add_child(widgy_site,
                   RawTextWidget,
                   text='left_2')

    subbucket = left.add_child(widgy_site,
                               Bucket)
    subbucket.add_child(widgy_site,
                        RawTextWidget,
                        text='subbucket_1')
    subbucket.add_child(widgy_site,
                        RawTextWidget,
                        text='subbucket_2')

    right.add_child(widgy_site,
                    RawTextWidget,
                    text='right_1')
    right.add_child(widgy_site,
                    RawTextWidget,
                    text='right_2')

    return left.node, right.node
