var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var nodes = requirejs('nodes/nodes'),
    _ = requirejs('underscore');

var assertListsEqual = function(a, b) {
  return assert(_.isEqual(a, b));
};

// define a TestComponent
var TestContent;
requirejs.define('components/testcomponent/component', ['widgy.contents', 'widgets/widgets'], function(contents, widgets) {
  TestContent = contents.Content.extend({
    viewClass: widgets.WidgetView
  });

  return TestContent;
});


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
    it('goes and finds its component', function(done) {
      var node = new nodes.Node({
        content: {
          component: 'testcomponent'
        }
      });

      node.on('load:content', function() {
        assert.instanceOf(node.content, TestContent);
        done();
      });
    });

    it('updates the content', function(done) {
      var node = new nodes.Node({
        content: {
          component: 'testcomponent',
          title: 'foo',
          test: 'foo'
        }
      });

      node.on('load:content', function() {
        assert.equal(node.content.get('title'), 'foo');
        assert.equal(node.content.get('test'), 'foo');

        node.set({content: { title: 'bar' } });

        assert.equal(node.content.get('title'), 'bar');
        assert.equal(node.content.get('test'), 'foo');
        done();
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

  it('update updates content too', function(done) {
    var count = 0,
        x = new nodes.NodeCollection([
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

    x.on('load:content', function() {
      // wait until both are ready.
      if ( ++count < 2 )
        return;
      x.off('load:content');

      var node1 = x.get(1);
      assert.equal(node1.children.length, 1);

      x.update2([
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

      assert.equal(node1.content.get('test'), 'bar');

      // non destructive merge.
      assert.strictEqual(node1, x.get(1));

      // remove old ones
      assert.isUndefined(x.get(2));

      // add new ones
      var node3 = x.get(3);
      assert.isObject(node3);
      node3.on('load:content', function() {
        assert.equal(node3.content.get('test'), 'baz');
      });

      // and do children too.
      assert.equal(node1.children.length, 2);
      assertListsEqual(node1.children.pluck('test'), [1, 2]);

      done();
    });
  });
});
