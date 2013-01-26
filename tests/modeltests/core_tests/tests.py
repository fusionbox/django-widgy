import json
from pprint import pprint

from django.test import TestCase
from django.contrib.auth.models import User
from django import forms
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType

from widgy.models import Node, UnknownWidget, VersionTracker
from widgy.views import extract_id
from widgy.exceptions import (ParentWasRejected, ChildWasRejected,
                              MutualRejection, InvalidTreeMovement)

from .widgy_config import widgy_site
from .models import (Layout, Bucket, RawTextWidget, CantGoAnywhereWidget,
                     PickyBucket, ImmovableBucket, HasAWidgy, AnotherLayout,
                     HasAWidgyOnlyAnotherLayout, VowelBucket)


class RootNodeTestCase(TestCase):
    urls = 'modeltests.core_tests.urls'

    def setUp(self):
        self.root_node = Layout.add_root(widgy_site).node


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

    def test_to_json_works_for_multi_table_inheritance(self):
        picky_bucket = self.root_node.content.add_child(widgy_site,
                                                        PickyBucket)
        picky_bucket.to_json(widgy_site)

    def test_reposition(self):
        left, right = make_a_nice_tree(self.root_node)

        with self.assertRaises(InvalidTreeMovement):
            self.root_node.content.reposition(widgy_site, parent=left.content)

        with self.assertRaises(InvalidTreeMovement):
            left.content.reposition(widgy_site, right=self.root_node.content)

        # swap left and right
        right.content.reposition(widgy_site, right=left.content)

        new_left, new_right = self.root_node.get_children()
        self.assertEqual(right, new_left)
        self.assertEqual(left, new_right)

        raw_text = new_right.get_first_child()
        with self.assertRaises(ChildWasRejected):
            raw_text.content.reposition(widgy_site, parent=self.root_node.content, right=new_left.content)

        subbucket = list(new_right.get_children())[-1]
        subbucket.content.reposition(widgy_site, parent=self.root_node.content, right=new_left.content)
        new_subbucket, new_left, new_right = self.root_node.get_children()
        self.assertEqual(new_subbucket, subbucket)

    def test_proxy_model(self):
        bucket = VowelBucket.add_root(widgy_site)
        bucket = Node.objects.get(pk=bucket.node.pk).content
        bucket.add_child(widgy_site, ImmovableBucket)

        with self.assertRaises(ChildWasRejected):
            bucket.add_child(widgy_site, Bucket)

        bucket.add_child(widgy_site, ImmovableBucket)
        with self.assertRaises(ChildWasRejected):
            bucket.add_child(widgy_site, Bucket)

    def test_unkown_content_type(self):
        """
        A node with a ContentType whose model class can not be found should use
        an UnknownWidget in its place
        """
        fake_ct = ContentType.objects.create(
            name='fake',
            app_label='faaaaake',
        )
        self.root_node.content_type = fake_ct
        self.root_node.save()

        root_node = Node.objects.get(pk=self.root_node.pk)
        self.assertIsInstance(root_node.content, UnknownWidget)

    def test_unkown_content_type_prefetch(self):
        """
        prefetch_tree follows a different code path, so test it too
        """

        fake_ct = ContentType.objects.create(
            name='fake',
            app_label='faaaaake',
        )

        left, right = make_a_nice_tree(self.root_node)
        left.content_type = fake_ct
        left.save()

        root_node = Node.objects.get(pk=self.root_node.pk)
        root_node.prefetch_tree()
        self.assertIsInstance(list(root_node.content.get_children())[0].node.content, UnknownWidget)


class TestVersioning(RootNodeTestCase):
    def test_clone_tree(self):
        left, right = make_a_nice_tree(self.root_node)

        new_tree = self.root_node.clone_tree()
        for a, b in zip(self.root_node.depth_first_order(),
                        new_tree.depth_first_order()):
            self.assertEqual(a.numchild, b.numchild)
            self.assertEqual(a.content_type_id, b.content_type_id)
            a_dict = model_to_dict(a.content)
            b_dict = model_to_dict(b.content)
            del a_dict['id']
            del b_dict['id']
            self.assertEqual(a_dict, b_dict)

    def test_commit(self):
        root_node = RawTextWidget.add_root(widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit1 = tracker.commit()

        self.assertNotEqual(tracker.working_copy, root_node)

        textwidget_content = tracker.working_copy.content
        textwidget_content.text = 'second'
        textwidget_content.save()
        commit2 = tracker.commit()

        self.assertEqual(commit1.root_node.content.text, 'first')
        self.assertEqual(commit2.root_node.content.text, 'second')

        self.assertEqual(commit2.parent, commit1)
        self.assertEqual(tracker.head, commit2)

    def test_tree_structure_versioned(self):
        root_node = Bucket.add_root(widgy_site).node
        root_node.content.add_child(
            widgy_site,
            RawTextWidget,
            text='a')
        root_node.content.add_child(
            widgy_site,
            RawTextWidget,
            text='b')

        # if the root_node isn't refetched, get_children is somehow empty. I
        # don't know why
        root_node = Node.objects.get(pk=root_node.pk)
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit1 = tracker.commit()

        new_a, new_b = tracker.working_copy.content.get_children()
        new_b.reposition(widgy_site, right=new_a)
        commit2 = tracker.commit()
        self.assertEqual(['a', 'b'],
                         [i.content.text for i in commit1.root_node.get_children()])
        self.assertEqual(['b', 'a'],
                         [i.content.text for i in commit2.root_node.get_children()])


    def test_revert(self):
        root_node = RawTextWidget.add_root(widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)
        commit1 = tracker.commit()

        self.assertNotEqual(tracker.working_copy, root_node)

        textwidget_content = tracker.working_copy.content
        textwidget_content.text = 'second'
        textwidget_content.save()
        commit2 = tracker.commit()

        commit3 = tracker.revert_to(commit1)

        textwidget_content = tracker.working_copy.content
        textwidget_content.text = 'fourth'
        textwidget_content.save()

        commit4 = tracker.commit()

        self.assertEqual(['fourth', 'first', 'second', 'first'],
                         [i.root_node.content.text for i in tracker.get_history()])

    def test_get_history(self):
        root_node = RawTextWidget.add_root(widgy_site, text='first').node
        tracker = VersionTracker.objects.create(working_copy=root_node)

        commits = reversed([tracker.commit() for i in range(6)])

        self.assertSequenceEqual(list(tracker.get_history()), list(commits))


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
            self.assertEqual(left.get_children()[0].get_ancestors(), [root_node.content, left])
            self.assertEqual(
                left.get_children()[2].get_children()[0].get_ancestors(),
                [root_node.content, left, left.get_children()[2]])

            self.assertEqual(left.get_root(), left.get_parent())
            self.assertEqual(left.get_children()[0].get_root(), left.get_parent())
            self.assertEqual(root_node.get_root(), root_node)

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

            self.assertEqual(left.get_root(), left.get_parent())
            self.assertEqual(list(left.get_children())[0].get_root(), left.get_parent())

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
        self.assertEqual(left.get_children()[0].get_ancestors(), [left.get_parent(), left])

        self.assertEqual(left.get_root(), left.get_parent())
        self.assertEqual(left.get_children()[0].get_root(), left.get_parent())


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
        new_child = json.loads(new_child.content)['node']
        self.assertEqual(new_child['parent_id'], bucket['url'])
        self.assertEqual(new_child['content']['__class__'], 'core_tests.rawtextwidget')

        db_bucket = Node.objects.get(id=extract_id(bucket['url']))
        self.assertEqual(db_bucket.get_children_count(), 1)

        new_child['content']['attributes']['text'] = 'foobar'
        r = self.put(new_child['content']['url'], new_child['content'])
        self.assertEqual(r.status_code, 200)

        r = self.get(new_child['content']['url'])
        self.assertEqual(r.status_code, 200)
        textcontent = json.loads(r.content)
        self.assertEqual(textcontent['attributes']['text'], 'foobar')

        # move the node to the other bucket
        new_child['parent_id'] = self.root_node.to_json(widgy_site)['children'][1]['url']
        r = self.put(new_child['url'], new_child)
        self.assertEqual(r.status_code, 200)

    def test_delete(self):
        left, right = make_a_nice_tree(self.root_node)
        number_of_nodes = Node.objects.count()
        number_of_right_nodes = len(right.get_descendants()) + 1
        content = right.content
        r = self.delete(right.get_api_url(widgy_site))
        self.assertEqual(r.status_code, 200)

        with self.assertRaises(Node.DoesNotExist):
            Node.objects.get(pk=right.pk)

        with self.assertRaises(type(content).DoesNotExist):
            type(content).objects.get(pk=content.pk)

        self.assertEqual(Node.objects.count(), number_of_nodes - number_of_right_nodes)

    def test_reposition_immovable(self):
        left, right = make_a_nice_tree(self.root_node)
        bucket = left.content.add_child(widgy_site, ImmovableBucket)

        resp = self.put(bucket.node.get_api_url(widgy_site), {
            'right_id': None,
            'parent_id': right.get_api_url(widgy_site),
        })
        self.assertEquals(resp.status_code, 409)

    def test_available_children(self):
        left, right = make_a_nice_tree(self.root_node)
        subbucket = list(left.get_children())[-1]
        resp = self.get(self.root_node.to_json(widgy_site)['available_children_url'])
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)

        def select(cls_name):
            possible_parent_urls = []
            for node_url, child_classes in data.iteritems():
                for i in child_classes:
                    if i['__class__'] == cls_name:
                        possible_parent_urls.append(node_url)
            return possible_parent_urls

        bucket_parents = select('core_tests.bucket')
        immovablebucket_parents = select('core_tests.immovablebucket')
        pickybucket_parents = select('core_tests.pickybucket')
        rawtext_parents = select('core_tests.rawtextwidget')
        cantgoanywhere_parents = select('core_tests.cantgoanywherewidget')

        def lists_equal(instances, urls):
            urls = sorted(map(str, urls))
            instance_urls = sorted(str(i.get_api_url(widgy_site)) for i in instances)
            self.assertEqual(instance_urls, urls)

        lists_equal([], cantgoanywhere_parents)
        lists_equal([right, left, subbucket, self.root_node], bucket_parents)
        lists_equal([right, left, subbucket, self.root_node], immovablebucket_parents)
        lists_equal([right, left, subbucket, self.root_node], pickybucket_parents)
        lists_equal([right, left, subbucket], rawtext_parents)

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

    def test_possible_parents(self):
        def order_ignorant_equals(a, b):
            self.assertEqual(sorted(a), sorted(b))

        left, right = make_a_nice_tree(self.root_node)

        resp = self.get(self.root_node.to_json(widgy_site)['possible_parents_url'])
        possible_parents = json.loads(resp.content)
        order_ignorant_equals([], possible_parents)

        resp = self.get(left.to_json(widgy_site)['possible_parents_url'])
        possible_parents = json.loads(resp.content)
        order_ignorant_equals([right.get_api_url(widgy_site),
                               self.root_node.get_api_url(widgy_site)],
                              possible_parents)

        resp = self.get(right.to_json(widgy_site)['possible_parents_url'])
        possible_parents = json.loads(resp.content)
        order_ignorant_equals([left.get_api_url(widgy_site),
                               self.root_node.get_api_url(widgy_site),
                               left.content.get_children()[2].node.get_api_url(widgy_site)],
                              possible_parents)

        resp = self.get(left.content.get_children()[0].node.to_json(widgy_site)['possible_parents_url'])
        possible_parents = json.loads(resp.content)
        order_ignorant_equals([left.get_api_url(widgy_site),
                               right.get_api_url(widgy_site),
                               left.content.get_children()[2].node.get_api_url(widgy_site)],
                              possible_parents)

    def test_optimized_compatibility_fetching(self):
        left, right = make_a_nice_tree(self.root_node)

        # loads . dumps == normalize the types to what json uses, list vs tuple
        left_json = json.loads(json.dumps(left.to_json(widgy_site)))
        left_url = left_json['url']
        root_json = json.loads(json.dumps(self.root_node.to_json(widgy_site)))
        root_url = root_json['url']

        def doit(method, *args):
            ret = json.loads(getattr(self, method)('{0}?include_compatibility_for={1}'.format(left_url, root_url), *args).content)
            compatibility = json.loads(self.get(root_json['available_children_url']).content)

            if method == 'get':
                self.assertEqual(left_json, ret['node'])

            self.assertEqual(compatibility, ret['compatibility'])

        doit('get')
        doit('post', {
            '__class__': 'core_tests.rawtextwidget',
            'parent_id': left_url,
            'right_id': None,
        })
        doit('put', left_json)
        doit('delete')
