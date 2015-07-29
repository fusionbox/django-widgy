from __future__ import absolute_import
from operator import itemgetter
from itertools import chain
import json
import imp

import mock

from django.core import urlresolvers
from django.utils.functional import cached_property
from django.core.exceptions import PermissionDenied
from django.conf import settings

from widgy.views import extract_id
from widgy.models import Node

from ..widgy_config import widgy_site
from ..models import (
    Bucket, ImmovableBucket, UndeletableRawTextWidget, RawTextWidget, Layout,
    PickyBucket,
)
from .base import RootNodeTestCase, HttpTestCase, make_a_nice_tree, SwitchUserTestCase


def decode_json_request(req):
    return json.loads(req.content.decode(settings.DEFAULT_CHARSET))


class TestApi(RootNodeTestCase, HttpTestCase):
    widgy_site = widgy_site

    @cached_property
    def urls(self):
        urls = imp.new_module('urls')
        urls.urlpatterns = self.widgy_site.get_urls()
        return urls

    def setUp(self):
        super(TestApi, self).setUp()
        self.node_url = self.widgy_site.reverse(self.widgy_site.node_view)

    def test_add_child(self):
        bucket = self.root_node.to_json(self.widgy_site)['children'][0]
        db_bucket = Node.objects.get(id=extract_id(bucket['url']))
        self.assertEqual(db_bucket.get_children_count(), 0)

        new_child = self.post(self.node_url, {
            '__class__': 'core_tests.rawtextwidget',
            'parent_id': bucket['url'],
            'right_id': None,
        })

        self.assertEqual(new_child.status_code, 201)
        new_child = decode_json_request(new_child)['node']
        self.assertEqual(new_child['parent_id'], bucket['url'])
        self.assertEqual(new_child['content']['__class__'], 'core_tests.rawtextwidget')

        db_bucket = Node.objects.get(id=extract_id(bucket['url']))
        self.assertEqual(db_bucket.get_children_count(), 1)

        new_child['content']['attributes']['text'] = 'foobar'
        r = self.put(new_child['content']['url'], new_child['content'])
        self.assertEqual(r.status_code, 200)

        r = self.get(new_child['content']['url'])
        self.assertEqual(r.status_code, 200)
        textcontent = decode_json_request(r)
        self.assertEqual(textcontent['attributes']['text'], 'foobar')

        # move the node to the other bucket
        new_child['parent_id'] = self.root_node.to_json(self.widgy_site)['children'][1]['url']
        r = self.put(new_child['url'], new_child)
        self.assertEqual(r.status_code, 200)

    def test_validation_error(self):
        left, right = make_a_nice_tree(self.root_node, self.widgy_site)
        obj = RawTextWidget.objects.all()[0]
        url = obj.get_api_url(self.widgy_site)
        data = obj.to_json(self.widgy_site)
        data['attributes']['text'] = ''

        resp = self.put(url, data)
        self.assertEqual(resp.status_code, 409)
        # validation error for field name
        self.assertIn('text', decode_json_request(resp))

    def test_delete(self):
        left, right = make_a_nice_tree(self.root_node, self.widgy_site)
        number_of_nodes = Node.objects.count()
        number_of_right_nodes = len(right.get_descendants()) + 1
        right_children = right.content.depth_first_order()
        r = self.delete(right.get_api_url(self.widgy_site))
        self.assertEqual(r.status_code, 200)

        with self.assertRaises(Node.DoesNotExist):
            Node.objects.get(pk=right.pk)

        for should_be_deleted in right_children:
            self.assertFalse(type(should_be_deleted).objects.filter(pk=should_be_deleted.pk).exists())

        self.assertEqual(Node.objects.count(), number_of_nodes - number_of_right_nodes)

    def test_reposition_immovable(self):
        left, right = make_a_nice_tree(self.root_node, self.widgy_site)
        bucket = left.content.add_child(self.widgy_site, ImmovableBucket)

        resp = self.put(bucket.node.get_api_url(self.widgy_site), {
            'right_id': None,
            'parent_id': right.get_api_url(self.widgy_site),
        })
        self.assertEquals(resp.status_code, 409)

    def test_available_children(self):
        left, right = make_a_nice_tree(self.root_node, self.widgy_site)
        subbucket = list(left.get_children())[-1]
        resp = self.get(self.root_node.to_json(self.widgy_site)['available_children_url'])
        self.assertEqual(resp.status_code, 200)
        data = decode_json_request(resp)

        def select(cls_name):
            possible_parent_urls = []
            for node_url, child_classes in data.items():
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
            instance_urls = sorted(str(i.get_api_url(self.widgy_site)) for i in instances)
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
        for url_obj in self.widgy_site.get_urls():
            regex = url_obj.regex

            # Creates as many positional arguments as needed.
            args = ('a',) * (regex.groups - len(regex.groupindex))

            # Creates all the keyword arguments
            kwargs = dict((key, 'a') for key in regex.groupindex.keys())

            url = self.widgy_site.reverse(url_obj.callback, args=args, kwargs=kwargs)

            for method in self.client.options(url)['Allow'].lower().split(','):
                method = method.strip()

                # The view should call widgy_site.authorize_view before doing
                # anything.  If there is an exception raised here, it is likely
                # that the view didn't call widgy_site.authorize_view.
                with mock.patch.object(self.widgy_site, 'authorize_view') as authorize_mock:
                    authorize_mock.side_effect = PermissionDenied
                    resp = getattr(self.client, method)(url)
                    self.assertEqual(resp.status_code, 403)
                    self.assertEqual(authorize_mock.call_count, 1)


    def test_possible_parents(self):
        def order_ignorant_equals(a, b):
            self.assertEqual(sorted(a), sorted(b))

        left, right = make_a_nice_tree(self.root_node, self.widgy_site)

        resp = self.get(self.root_node.to_json(self.widgy_site)['possible_parents_url'])
        possible_parents = decode_json_request(resp)
        order_ignorant_equals([], possible_parents)

        resp = self.get(left.to_json(self.widgy_site)['possible_parents_url'])
        possible_parents = decode_json_request(resp)
        order_ignorant_equals([right.get_api_url(self.widgy_site),
                               self.root_node.get_api_url(self.widgy_site)],
                              possible_parents)

        resp = self.get(right.to_json(self.widgy_site)['possible_parents_url'])
        possible_parents = decode_json_request(resp)
        order_ignorant_equals([left.get_api_url(self.widgy_site),
                               self.root_node.get_api_url(self.widgy_site),
                               left.content.get_children()[2].node.get_api_url(self.widgy_site)],
                              possible_parents)

        resp = self.get(
            left.content.get_children()[0].node.to_json(self.widgy_site)['possible_parents_url'])
        possible_parents = decode_json_request(resp)
        order_ignorant_equals([left.get_api_url(self.widgy_site),
                               right.get_api_url(self.widgy_site),
                               left.content.get_children()[2].node.get_api_url(self.widgy_site)],
                              possible_parents)

    def test_optimized_compatibility_fetching(self):
        left, right = make_a_nice_tree(self.root_node, self.widgy_site)

        # loads . dumps == normalize the types to what json uses, list vs tuple
        left_json = json.loads(json.dumps(left.to_json(self.widgy_site)))
        left_url = left_json['url']
        root_json = json.loads(json.dumps(self.root_node.to_json(self.widgy_site)))
        root_url = root_json['url']

        def doit(method, *args):
            url = '{0}?include_compatibility_for={1}'.format(left_url, root_url)
            ret = decode_json_request(getattr(self, method)(url, *args))
            compatibility = decode_json_request(self.get(root_json['available_children_url']))

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
        node = UndeletableRawTextWidget.add_root(self.widgy_site,
                                                 text='asdf').node

        resp = self.delete(node.get_api_url(self.widgy_site))
        self.assertEqual(resp.status_code, 409)
        self.assertTrue(Node.objects.get(pk=node.pk))

    def test_node_templates_view(self):
        left, right = make_a_nice_tree(self.root_node, self.widgy_site)

        r = self.get(left.content.to_json(self.widgy_site)['template_url'])

        # not sure there's much else we can test here
        self.assertIn('<form', decode_json_request(r)['edit_template'])

    def test_editable_toggles_existence_of_edit_url(self):
        self.root_node.content.editable = True
        self.assertIn('edit_url', self.root_node.content.to_json(self.widgy_site))
        self.root_node.content.editable = False
        self.assertNotIn('edit_url', self.root_node.content.to_json(self.widgy_site))

    def test_node_edit_view(self):
        self.root_node.content.editable = True
        r = self.client.get(self.root_node.content.to_json(self.widgy_site)['edit_url'])
        self.assertEqual(r.status_code, 200)

        # this is a template view, so there's not much we can test.
        decoded_content = r.content.decode(settings.DEFAULT_CHARSET)
        self.assertIn('new Widgy', decoded_content)
        self.assertIn(urlresolvers.reverse(self.widgy_site.node_view), decoded_content)

    def test_node_404(self):
        left, right = make_a_nice_tree(self.root_node, self.widgy_site)

        before_json = self.root_node.to_json(self.widgy_site)
        # make a fake url
        right.pk += 9000
        r = self.put(left.get_api_url(self.widgy_site), {
            'right_id': None,
            'parent_id': right.get_api_url(self.widgy_site),
        })
        right.pk -= 9000

        self.assertEqual(r.status_code, 404)

        self.assertEqual(before_json, Node.objects.get(pk=self.root_node.pk).to_json(self.widgy_site))

    def test_nonexistant_content_type(self):
        new_child = self.post(self.node_url, {
            '__class__': 'corcwaasdfe_tests.rawtextwidgetasdfa1',
            'parent_id': None,
            'right_id': None,
        })

        self.assertEqual(new_child.status_code, 404)

    def test_add_with_right_id(self):
        left, right = make_a_nice_tree(self.root_node, self.widgy_site)

        before_children = len(left.get_children())
        new_child = self.post(self.node_url, {
            '__class__': 'core_tests.rawtextwidget',
            'right_id': left.get_children()[0].get_api_url(self.widgy_site),
        })

        self.assertEqual(new_child.status_code, 201)

        left = Node.objects.get(pk=left.pk)
        self.assertEqual(before_children + 1, len(left.get_children()))


class PermissionsTest(SwitchUserTestCase, RootNodeTestCase, HttpTestCase):
    widgy_site = widgy_site

    def setUp(self):
        super(PermissionsTest, self).setUp()
        # delete those autocreated buckets
        for bucket in Bucket.objects.all():
            bucket.delete()

    def extractAvailableChildren(self, data):
        return map(itemgetter('__class__'), chain.from_iterable(data.values()))

    def assertCompatibilityContains(self, key, data):
        return self.assertIn(key, self.extractAvailableChildren(data))

    def assertCompatibilityNotContains(self, key, data):
        return self.assertNotIn(key, self.extractAvailableChildren(data))

    def test_available_children(self):
        def doit():
            url = self.root_node.to_json(self.widgy_site)['available_children_url']
            return self.get(url)

        def fail():
            resp = doit()
            self.assertEqual(resp.status_code, 403)

        def win():
            resp = doit()
            self.assertEqual(resp.status_code, 200)
            data = decode_json_request(resp)
            self.assertCompatibilityContains('core_tests.bucket', data)

        fail()  # not logged in

        with self.as_staffuser() as user:
            resp = doit()  # staff, no permissions
            self.assertEqual(resp.status_code, 200)
            data = decode_json_request(resp)
            self.assertCompatibilityNotContains('core_tests.bucket', data)
            self.assertEqual(data, {self.root_node.get_api_url(self.widgy_site): []})

        with self.as_staffuser() as user:
            with self.with_permission(user, 'add', Bucket):
                win()  # staff, with permissions

        with self.as_superuser():
            win()  # superuser

    def as_different_types_of_user(self, permissionsargs, fail, win):
        fail()  # not logged in

        with self.logged_in() as user:
            fail()  # not staff

        with self.as_staffuser() as user:
            fail()  # staff, no permissions

        with self.as_staffuser() as user:
            with self.with_permission(user, *permissionsargs):
                win()  # staff, with permissions

        with self.as_superuser():
            win()  # superuser

    def test_add_node(self):
        def doit():
            url = urlresolvers.reverse(self.widgy_site.node_view)
            return self.post(url, {
                '__class__': 'core_tests.bucket',
                'right_id': None,
                'parent_id': self.root_node.get_api_url(self.widgy_site),
            })

        def fail():
            before = Bucket.objects.count()
            resp = doit()
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(Bucket.objects.count(), before)

        def win():
            before = Bucket.objects.count()
            resp = doit()
            self.assertEqual(resp.status_code, 201)
            self.assertEqual(Bucket.objects.count(), before + 1)

            # reset
            Bucket.objects.get().delete()

        self.as_different_types_of_user(('add', Bucket), fail, win)

    def test_move_node(self):
        left = self.root_node.content.add_child(self.widgy_site, Bucket)
        right = self.root_node.content.add_child(self.widgy_site, PickyBucket)

        data = {
            '__class__': 'core_tests.bucket',
            'right_id': left.node.get_api_url(self.widgy_site),
            'parent_id': self.root_node.get_api_url(self.widgy_site),
        }

        def doit():
            url = right.node.get_api_url(self.widgy_site)
            return self.put(url, data)

        def fail():
            resp = doit()
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(list(Layout.objects.get().get_children()),
                             [left, right])

        def win():
            resp = doit()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(list(Layout.objects.get().get_children()),
                             [right, left])

            node_data = decode_json_request(resp)['node']
            self.assertEqual(node_data['right_id'], data['right_id'])
            self.assertEqual(node_data['parent_id'], data['parent_id'])

            # reset
            PickyBucket.objects.get().reposition(self.widgy_site, parent=self.root_node.content)

        self.as_different_types_of_user(('change', PickyBucket), fail, win)

    def test_delete_node(self):
        # we need to mutate this to reset
        _left = [self.root_node.content.add_child(self.widgy_site, Bucket)]

        def doit():
            url = _left[0].node.get_api_url(self.widgy_site)
            return self.delete(url)

        def fail():
            before = Bucket.objects.count()
            resp = doit()
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(Bucket.objects.count(), before)

        def win():
            before = Bucket.objects.count()
            resp = doit()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(Bucket.objects.count(), before - 1)
            # reset
            _left[0] = self.root_node.content.add_child(self.widgy_site, Bucket)

        self.as_different_types_of_user(('delete', Bucket), fail, win)

    def test_delete_deep_node(self):
        self.root_node.content.add_child(self.widgy_site, Bucket)

        with self.as_staffuser() as user:
            with self.with_permission(user, 'delete', Layout):
                url = self.root_node.get_api_url(self.widgy_site)
                resp = self.delete(url)
                self.assertEqual(resp.status_code, 403)
                self.assertTrue(Bucket.objects.exists())

    def test_edit_content(self):
        content = RawTextWidget.add_root(self.widgy_site)
        content.text = 'hello'
        content.save()

        def doit():
            url = content.to_json(self.widgy_site)['url']
            return self.put(url, {
                'attributes': {'text': 'goodbye'},
            })

        def fail():
            resp = doit()
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(RawTextWidget.objects.get().text, 'hello')

        def win():
            resp = doit()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(RawTextWidget.objects.get().text, 'goodbye')
            # reset
            RawTextWidget.objects.update(text='hello')

        self.as_different_types_of_user(('change', RawTextWidget), fail, win)

    def test_templates_view(self):
        def doit():
            url = self.root_node.content.to_json(self.widgy_site)['template_url']
            return self.get(url)

        def fail():
            resp = doit()
            self.assertEqual(resp.status_code, 403)

        def win():
            resp = doit()
            self.assertEqual(resp.status_code, 200)

        self.as_different_types_of_user(('change', Layout), fail, win)

    def test_parents_view(self):
        """
        You only need to be able to see where a widget can go if you can
        move it.
        """
        bucket = self.root_node.content.add_child(self.widgy_site, PickyBucket)

        def doit():
            url = bucket.node.to_json(self.widgy_site)['possible_parents_url']
            return self.get(url)

        def fail():
            resp = doit()
            self.assertEqual(resp.status_code, 403)

        def win():
            resp = doit()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(decode_json_request(resp), [self.root_node.get_api_url(self.widgy_site)])

        self.as_different_types_of_user(('change', PickyBucket), fail, win)

    def test_node_edit_view(self):
        bucket = self.root_node.content.add_child(self.widgy_site, PickyBucket)

        def doit():
            bucket.editable = True
            url = bucket.to_json(self.widgy_site)['edit_url']
            # not a JSON view
            return self.client.get(url)

        def fail():
            resp = doit()
            self.assertIn(resp.status_code, (403, 302))

        def win():
            resp = doit()
            self.assertEqual(resp.status_code, 200)

        self.as_different_types_of_user(('change', Node), fail, win)

    def test_node_edit_view_staff_only(self):
        bucket = self.root_node.content.add_child(self.widgy_site, PickyBucket)
        bucket.editable = True
        url = bucket.to_json(self.widgy_site)['edit_url']
        with self.logged_in():
            with self.with_permission(self.user, 'change', bucket.node):
                response =  self.client.get(url)
        self.assertEqual(response.status_code, 403)
