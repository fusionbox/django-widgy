import json
from pprint import pprint

from django.test import TestCase
from django.contrib.auth.models import User
from django import forms
from django.contrib.contenttypes.models import ContentType

from widgy.models import Node
from widgy.views import extract_id
from widgy.exceptions import (ParentWasRejected, ChildWasRejected,
                              MutualRejection, InvalidTreeMovement)

from .widgy_config import widgy_site
from .models import (Layout, Bucket, RawTextWidget, CantGoAnywhereWidget,
                     PickyBucket, ImmovableBucket, HasAWidgy, AnotherLayout,
                     HasAWidgyOnlyAnotherLayout)


class RootNodeTestCase(TestCase):
    urls = 'modeltests.core_tests.urls'

    def setUp(self):
        self.root_node = Layout.add_root(widgy_site).node


def tree_to_dot(node):
    output = []
    output.append('digraph {')
    for i in [node] + list(node.get_descendants().order_by('path')):
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


class TestCore(RootNodeTestCase):
    def test_post_create(self):
        """
        Content.post_create should be called after creating a content.
        """
        self.assertEqual(len(self.root_node.get_children()), 2)

    def test_deep(self):
        """
        A tree should be able to be at least 50 levels deep.
        """
        content = self.root_node.content
        for i in range(50):
            content = content.add_child(widgy_site,
                                        Bucket)

        # + 2 -- original buckets
        self.assertEqual(len(self.root_node.get_descendants()), 50 + 2)

    def test_validate_relationship_cls(self):
        with self.assertRaises(ChildWasRejected):
            widgy_site.validate_relationship(self.root_node.content, RawTextWidget)

        bucket = list(self.root_node.content.get_children())[0]
        with self.assertRaises(ParentWasRejected):
            widgy_site.validate_relationship(bucket, CantGoAnywhereWidget)

        with self.assertRaises(MutualRejection):
            widgy_site.validate_relationship(self.root_node.content, CantGoAnywhereWidget)

    def test_validate_relationship_instance(self):
        picky_bucket = self.root_node.content.add_child(widgy_site,
                                                        PickyBucket)

        with self.assertRaises(ChildWasRejected):
            picky_bucket.add_child(widgy_site,
                                   RawTextWidget,
                                   text='aasdf')

        picky_bucket.add_child(widgy_site,
                               RawTextWidget,
                               text='hello')

        with self.assertRaises(ChildWasRejected):
            picky_bucket.add_child(widgy_site,
                                   Layout)

    def test_reposition(self):
        left, right = make_a_nice_tree(self.root_node)

        with self.assertRaises(InvalidTreeMovement):
            self.root_node.reposition(widgy_site, parent=left)

        with self.assertRaises(InvalidTreeMovement):
            left.reposition(widgy_site, right=self.root_node)

        # swap left and right
        right.reposition(widgy_site, right=left)

        new_left, new_right = self.root_node.get_children()
        self.assertEqual(right, new_left)
        self.assertEqual(left, new_right)

        raw_text = new_right.get_first_child()
        with self.assertRaises(ChildWasRejected):
            raw_text.reposition(widgy_site, parent=self.root_node, right=new_left)

        subbucket = list(new_right.get_children())[-1]
        subbucket.reposition(widgy_site, parent=self.root_node, right=new_left)
        new_subbucket, new_left, new_right = self.root_node.get_children()
        self.assertEqual(new_subbucket, subbucket)

    def test_reposition_immovable(self):
        left, right = make_a_nice_tree(self.root_node)
        bucket = left.content.add_child(widgy_site, ImmovableBucket)

        with self.assertRaises(InvalidTreeMovement):
            bucket.node.reposition(widgy_site, parent=self.root_node,
                                   right=left)


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


class TestPrefetchTree(RootNodeTestCase):
    def setUp(self):
        super(TestPrefetchTree, self).setUp()
        make_a_nice_tree(self.root_node)

    def test_prefetch_tree(self):
        with self.assertNumQueries(1):
            root_node = Node.objects.get(pk=self.root_node.pk)

        # 5 queries:
        #  - get descendants of root_node
        #  - get content types
        #  - get bucket contents
        #  - get layout contents
        #  - get text contents
        with self.assertNumQueries(5):
            root_node.prefetch_tree()

        # maybe_prefetch_tree shouldn't prefetch the tree again
        with self.assertNumQueries(0):
            root_node.maybe_prefetch_tree()

        # we have the tree, verify its structure without executing any
        # queries
        with self.assertNumQueries(0):
            left, right = root_node.content.get_children()
            left_children = list(left.get_children())
            self.assertEqual(left_children[0].text, 'left_1')
            self.assertEqual(left_children[1].text, 'left_2')
            subbucket = left_children[2]
            subbucket_children = list(subbucket.get_children())
            self.assertEqual(subbucket_children[0].text, 'subbucket_1')
            self.assertEqual(subbucket_children[1].text, 'subbucket_2')

            right_children = list(right.get_children())
            self.assertEqual(right_children[0].text, 'right_1')
            self.assertEqual(right_children[1].text, 'right_2')

        # verify some convience methods are prefetched as well
        with self.assertNumQueries(0):
            # on the Content
            left, right = root_node.content.get_children()
            self.assertEqual(left.get_next_sibling(), right)
            self.assertEqual(right.get_next_sibling(), None)
            self.assertEqual(right.get_parent(), root_node.content)
            self.assertEqual(root_node.content.get_parent(), None)
            self.assertEqual(root_node.content.get_next_sibling(), None)
            self.assertEqual(left.get_ancestors(), [root_node.content])
            self.assertEqual(left.children[0].get_ancestors(), [root_node.content, left])
            self.assertEqual(
                left.children[2].children[0].get_ancestors(),
                [root_node.content, left, left.children[2]])

            # on the Node
            left, right = root_node.get_children()
            self.assertEqual(left.get_parent(), root_node)
            self.assertEqual(left.get_next_sibling(), right)
            self.assertEqual(right.get_next_sibling(), None)
            self.assertEqual(root_node.get_parent(), None)
            self.assertEqual(root_node.get_next_sibling(), None)
            # list() because get_ancestors() returns a querysetish thing
            self.assertEqual(list(root_node.get_ancestors()), [])
            self.assertEqual(list(left.get_ancestors()), [root_node])
            self.assertEqual(list(list(left.get_children())[0].get_ancestors()), [root_node, left])

        # to_json shouldn't do any more queries either
        with self.assertNumQueries(0):
            root_node.to_json(widgy_site)

    def test_works_on_not_root_node(self):
        left_node = self.root_node.get_first_child()

        # 4 queries:
        #  - get descendants
        #  - get content types
        #  - get bucket contents
        #  - get text contents
        with self.assertNumQueries(4):
            left_node.prefetch_tree()

        with self.assertNumQueries(0):
            left = left_node.content
            left_children = list(left.get_children())
            self.assertEqual(left_children[0].text, 'left_1')
            self.assertEqual(left_children[1].text, 'left_2')
            subbucket = left_children[2]
            subbucket_children = list(subbucket.get_children())
            self.assertEqual(subbucket_children[0].text, 'subbucket_1')
            self.assertEqual(subbucket_children[1].text, 'subbucket_2')

        # For a non-root node, the parent and next sibling can't be computed by
        # prefetch_tree without another query for each one, so they may as well
        # be lazy
        right_node = list(self.root_node.get_children())[1]
        with self.assertNumQueries(2):
            self.assertEqual(left_node.get_parent(), self.root_node)
            self.assertEqual(left_node.get_next_sibling(), right_node)

        # get_ancestors must work correctly for non-root nodes, but it can't be
        # prefetched
        self.assertEqual(left.get_ancestors(), [left.get_parent()])
        self.assertEqual(left.children[0].get_ancestors(), [left.get_parent(), left])


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


class TestApi(RootNodeTestCase, HttpTestCase):
    def setUp(self):
        super(TestApi, self).setUp()
        self.node_url = widgy_site.reverse(widgy_site.node_view)

    def test_textcontent_available(self):
        available_children = json.loads(
            self.get(self.root_node.to_json(widgy_site)['available_children_url']).content)
        self.assertIn('core_tests.rawtextwidget', [i['__class__'] for i in available_children])

    def test_add_child(self):
        bucket = self.root_node.to_json(widgy_site)['children'][0]
        db_bucket = Node.objects.get(id=extract_id(bucket['url']))
        self.assertEqual(db_bucket.get_children_count(), 0)

        new_child = self.post(self.node_url, {
            '__class__': 'core_tests.rawtextwidget',
            'parent_id': bucket['url'],
            'right_id': None,
        })

        self.assertEqual(new_child.status_code, 201)
        new_child = json.loads(new_child.content)
        self.assertEqual(new_child['parent_id'], bucket['url'])
        self.assertEqual(new_child['content']['__class__'], 'core_tests.rawtextwidget')

        db_bucket = Node.objects.get(id=extract_id(bucket['url']))
        self.assertEqual(db_bucket.get_children_count(), 1)

        new_child['content']['text'] = 'foobar'
        r = self.put(new_child['content']['url'], new_child['content'])
        self.assertEqual(r.status_code, 200)

        r = self.get(new_child['content']['url'])
        self.assertEqual(r.status_code, 200)
        textcontent = json.loads(r.content)
        self.assertEqual(textcontent['text'], 'foobar')

        # move the node to the other bucket
        new_child['parent_id'] = self.root_node.to_json(widgy_site)['children'][1]['url']
        r = self.put(new_child['url'], new_child)
        self.assertEqual(r.status_code, 200)

    def test_delete(self):
        left, right = make_a_nice_tree(self.root_node)
        number_of_nodes = Node.objects.count()
        number_of_right_nodes = len(right.get_descendants()) + 1
        r = self.delete(right.get_api_url(widgy_site))
        self.assertEqual(r.status_code, 200)

        with self.assertRaises(Node.DoesNotExist):
            Node.objects.get(pk=right.pk)

        self.assertEqual(Node.objects.count(), number_of_nodes - number_of_right_nodes)

    def test_available_children(self):
        left, right = make_a_nice_tree(self.root_node)
        subbucket = list(left.get_children())[-1]
        resp = self.get(self.root_node.to_json(widgy_site)['available_children_url'])
        self.assertEqual(resp.status_code, 200)
        available_children = json.loads(resp.content)

        def select(cls_name):
            for i in available_children:
                if i['__class__'] == cls_name:
                    return i
            assert False, "Couldn't find %r" % cls_name

        bucket_data = select('core_tests.bucket')
        immovablebucket_data = select('core_tests.immovablebucket')
        pickybucket_data = select('core_tests.pickybucket')
        rawtext_data = select('core_tests.rawtextwidget')

        self.assertRaises(AssertionError, select, 'core_tests.cantgoanywherewidget')

        def lists_equal(instances, urls):
            urls = sorted(map(str, urls))
            instance_urls = sorted(str(i.get_api_url(widgy_site)) for i in instances)
            self.assertEqual(instance_urls, urls)

        lists_equal([right, left, subbucket, self.root_node],
                    bucket_data['possible_parent_nodes'])
        lists_equal([right, left, subbucket, self.root_node],
                    immovablebucket_data['possible_parent_nodes'])
        lists_equal([right, left, subbucket, self.root_node],
                    pickybucket_data['possible_parent_nodes'])
        lists_equal([right, left, subbucket],
                    rawtext_data['possible_parent_nodes'])

    def test_unauthorized_access(self):
        """
        Verify each URL defined in the WidgySite uses the WidgySite.authorize
        method.  Figures out how to reverse the URL (hackily) using the
        RegexURLPattern and also tries to determine which methods a view
        supports using HTTP OPTIONS.  The kwargs passed into reverse, probably
        won't pass any validation, but if they are reaching validation, the
        test has failed already.
        """
        for url_obj in widgy_site.get_urls():
            regex = url_obj.regex

            # Creates as many positional arguments as needed.
            args = ('a',) * (regex.groups - len(regex.groupindex))

            # Creates all the keyword arguments
            kwargs = dict((key, 'a') for key in regex.groupindex.keys())

            url = widgy_site.reverse(url_obj.callback, args=args, kwargs=kwargs)

            for method in self.client.options(url)['Allow'].lower().split(','):
                method = method.strip()

                # The view should call widgy_site.authorize before doing
                # anything.  If there is an exception raised here, it is likely
                # that the view didn't call widgy_site.authorize.
                resp = getattr(self.client, method)(url, HTTP_COOKIE='unauthorized_access=1')

                self.assertEqual(resp.status_code, 403)
