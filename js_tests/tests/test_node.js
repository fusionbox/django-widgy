var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var nodes = requirejs('nodes/nodes'),
    _ = requirejs('underscore'),
    Q = requirejs('lib/q');

var assertListsEqual = function(a, b, message) {
  if ( ! _.isEqual(a, b) )
  {
    var err = new Error(message);
    err.expected = b.toString();
    err.actual = a.toString();

    throw err;
  }
};

var TestComponent = requirejs('components/testcomponent/component');


describe('Node', function() {
  it('creates children correctly', function() {
    var node = new nodes.Node();

    assert.isObject(node.children);

    node = new nodes.Node({
      children: [
        {a: 1},
        {a: 2}
      ]
    });

    assert.isObject(node.children);

    assertListsEqual(node.children.pluck('a'), [1, 2]);
  });

  describe('content setter', function() {
    it('goes and finds its component', function() {
      var node = new nodes.Node({
        content: {
          component: 'testcomponent'
        }
      });

      return node.ready(function() {
        assert.instanceOf(node.content, TestComponent.Model);
      });
    });

    it('updates the content', function() {
      var node = new nodes.Node({
        content: {
          component: 'testcomponent',
          title: 'foo',
          test: 'foo'
        }
      });

      return node.ready(function(node) {
        assert.equal(node.content.get('title'), 'foo');
        assert.equal(node.content.get('test'), 'foo');

        node.set({content: { title: 'bar' } });

        assert.equal(node.content.get('title'), 'bar');
        assert.equal(node.content.get('test'), 'foo');
      });
    });

    it.skip('doesn\'t have timing issues', function() {
      var node = new nodes.Node({
        content: {
          component: 'testcomponent',
          test: 'foo'
        }
      });

      node.set({content: { title: 'bar' } });

      return node.ready(function(node) {
        assert.equal(node.content.get('test'), 'bar');
      });
    });
  });

  describe('position getters', function() {
    it('correctly figures out right', function() {
      var node1 = new nodes.Node(),
          node2 = new nodes.Node(),
          node3 = new nodes.Node(),
          node4 = new nodes.Node(),
          coll = new nodes.NodeCollection([node1, node2, node3, node4]);

      assert.equal(node1.getRight(), node2);
      assert.equal(node2.getRight(), node3);
      assert.equal(node3.getRight(), node4);
      assert.equal(node4.getRight(), null);
    });

    it('correctly figures out parent', function() {
      var node1 = new nodes.Node(),
          node2 = new nodes.Node();

      node1.children.add(node2);

      assert.equal(node2.getParent(), node1);
    });
  });

  describe('getComponent', function() {
    it('retrieves the component', function() {
      var node = new nodes.Node();

      return node.getComponent('testcomponent').then(function(model) {
        assert.deepEqual(model.component, TestComponent);
      });
    });
  });
});


describe('NodeCollection', function() {
  it('sortByRight sorts correctly', function() {
    var x = new nodes.NodeCollection([
      {url: 2, right_id: 3},
      {url: 4, right_id: 5},
      {url: 3, right_id: 4},
      {url: 6, right_id: 7},
      {url: 9, right_id: null},
      {url: 8, right_id: 9},
      {url: 7, right_id: 8},
      {url: 1, right_id: 2},
      {url: 5, right_id: 6}
    ]);

    x.sortByRight();

    assertListsEqual(x.pluck('url'), [1, 2, 3, 4, 5, 6, 7, 8, 9]);
  });

  it('update updates content too', function() {
    var x = new nodes.NodeCollection([
          {
            url: 1,
            children: [
              {url: 12, test: 'foo'}
            ],
            content: {
              component: 'testcomponent',
              test: 'foo'
            }
          },
          {
            url: 2,
            content: {
              component: 'testcomponent',
              test: 'foo'
            }
          }
        ]);

    var node1 = x.get(1),
        node2 = x.get(2);
    assert.equal(node1.children.length, 1);

    return Q.all([node1.ready(), node2.ready()]).then(function() {
      x.set2([
        {
          url: 1,
          children: [
            {url: 12, test: 1},
            {url: 13, test: 2}
          ],
          content: {
            component: 'testcomponent',
            test: 'bar'
          }
        },
        {
          url: 3,
          content: {
            component: 'testcomponent',
            test: 'baz'
          }
        }
      ]);

      // non destructive merge.
      assert.strictEqual(node1, x.get(1));

      assert.equal(node1.content.get('test'), 'bar');

      // remove old ones
      assert.isUndefined(x.get(2));

      // add new ones
      var node3 = x.get(3);
      assert.isObject(node3);
      node3.ready(function() {
        assert.equal(node3.content.get('test'), 'baz');
      });

      // and do children too.
      assert.equal(node1.children.length, 2);
      assertListsEqual(node1.children.pluck('test'), [1, 2]);
    });
  });

  describe('reposition', function() {
    it('reorders correctly', function() {
      var coll = new nodes.NodeCollection([
        {url: 1, right_id: 2},
        {url: 2, right_id: 3},
        {url: 3, right_id: 4},
        {url: 4, right_id: null}
      ]);

      assertListsEqual(coll.pluck('url'), [1, 2, 3, 4]);

      var node2 = coll.get(2);
      node2.set('right_id', 1);
      coll.reposition(node2);
      assertListsEqual(coll.pluck('url'), [2, 1, 3, 4]);

      var node3 = coll.get(3);
      node3.set('right_id', null);
      coll.reposition(node3);
      assertListsEqual(coll.pluck('url'), [2, 1, 4, 3]);
    });

    it('works across collections', function() {
      var col1 = new nodes.NodeCollection([
            {url: 1, right_id: 2},
            {url: 2, right_id: 3},
            {url: 3, right_id: 4},
            {url: 4, right_id: null}
          ]),
          col2 = new nodes.NodeCollection([
            {url: 5, right_id: 6},
            {url: 6, right_id: 7},
            {url: 7, right_id: 8},
            {url: 8, right_id: null}
          ]);

      var node1 = col1.get(1);
      node1.set('right_id', 7);
      col2.reposition(node1);
      assertListsEqual(col1.pluck('url'), [2, 3, 4]);
      assertListsEqual(col2.pluck('url'), [5, 6, 1, 7, 8]);

      var node5 = col2.get(5);
      node5.set('right_id', null);
      col1.reposition(node5);
      assertListsEqual(col1.pluck('url'), [2, 3, 4, 5]);
      assertListsEqual(col2.pluck('url'), [6, 1, 7, 8]);
    });
  });
});
