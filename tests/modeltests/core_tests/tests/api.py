import json

from django.core import urlresolvers

from widgy.views import extract_id
from widgy.models import Node

from modeltests.core_tests.widgy_config import widgy_site
from modeltests.core_tests.models import ImmovableBucket, UndeletableRawTextWidget, RawTextWidget
from modeltests.core_tests.tests.base import RootNodeTestCase, HttpTestCase, make_a_nice_tree


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

    def test_validation_error(self):
        left, right = make_a_nice_tree(self.root_node)
        obj = RawTextWidget.objects.all()[0]
        url = obj.get_api_url(widgy_site)
        data = obj.to_json(widgy_site)
        data['attributes']['text'] = ''

        resp = self.put(url, data)
        self.assertEqual(resp.status_code, 409)
        # validation error for field name
        self.assertIn('text', json.loads(resp.content))

    def test_delete(self):
        left, right = make_a_nice_tree(self.root_node)
        number_of_nodes = Node.objects.count()
        number_of_right_nodes = len(right.get_descendants()) + 1
        right_children = right.content.depth_first_order()
        r = self.delete(right.get_api_url(widgy_site))
        self.assertEqual(r.status_code, 200)

        with self.assertRaises(Node.DoesNotExist):
            Node.objects.get(pk=right.pk)

        for should_be_deleted in right_children:
            self.assertFalse(type(should_be_deleted).objects.filter(pk=should_be_deleted.pk).exists())

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

        resp = self.get(
            left.content.get_children()[0].node.to_json(widgy_site)['possible_parents_url'])
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
            url = '{0}?include_compatibility_for={1}'.format(left_url, root_url)
            ret = json.loads(getattr(self, method)(url, *args).content)
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

    def test_delete_undeletable(self):
        node = UndeletableRawTextWidget.add_root(widgy_site,
                                                 text='asdf').node

        resp = self.delete(node.get_api_url(widgy_site))
        self.assertEqual(resp.status_code, 409)
        self.assertTrue(Node.objects.get(pk=node.pk))

    def test_node_templates_view(self):
        left, right = make_a_nice_tree(self.root_node)

        r = self.get(left.content.to_json(widgy_site)['template_url'])

        # not sure there's much else we can test here
        self.assertIn('<form', json.loads(r.content)['edit_template'])

    def test_editable_toggles_existence_of_edit_url(self):
        self.root_node.content.editable = True
        self.assertIn('edit_url', self.root_node.content.to_json(widgy_site))
        self.root_node.content.editable = False
        self.assertNotIn('edit_url', self.root_node.content.to_json(widgy_site))

    def test_node_edit_view(self):
        self.root_node.content.editable = True
        r = self.client.get(self.root_node.content.to_json(widgy_site)['edit_url'])
        self.assertEqual(r.status_code, 200)

        # this is a template view, so there's not much we can test.
        self.assertIn('new Widgy', r.content)
        self.assertIn(urlresolvers.reverse(widgy_site.node_view), r.content)

    def test_node_404(self):
        left, right = make_a_nice_tree(self.root_node)

        before_json = self.root_node.to_json(widgy_site)
        # make a fake url
        right.pk += 9000
        r = self.put(left.get_api_url(widgy_site), {
            'right_id': None,
            'parent_id': right.get_api_url(widgy_site),
        })
        right.pk -= 9000

        self.assertEqual(r.status_code, 404)

        self.assertEqual(before_json, Node.objects.get(pk=self.root_node.pk).to_json(widgy_site))

    def test_nonexistant_content_type(self):
        new_child = self.post(self.node_url, {
            '__class__': 'corcwaasdfe_tests.rawtextwidgetasdfa1',
            'parent_id': None,
            'right_id': None,
        })

        self.assertEqual(new_child.status_code, 404)

    def test_add_with_right_id(self):
        left, right = make_a_nice_tree(self.root_node)

        before_children = len(left.get_children())
        new_child = self.post(self.node_url, {
            '__class__': 'core_tests.rawtextwidget',
            'right_id': left.get_children()[0].get_api_url(widgy_site),
        })

        self.assertEqual(new_child.status_code, 201)

        left = Node.objects.get(pk=left.pk)
        self.assertEqual(before_children + 1, len(left.get_children()))
