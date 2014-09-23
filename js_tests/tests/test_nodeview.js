var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert,
    sinon = require('sinon');

var nodes = requirejs('nodes/nodes'),
    widgy = requirejs('widgy'),
    shelves = requirejs('shelves/shelves'),
    _ = requirejs('underscore'),
    Q = requirejs('lib/q');


describe('ShelfView', function() {
  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent',
        shelf: true
      }
    });
  });

  it('bubbles ShelfItemView events', function() {
    return this.node.ready(function(node) {
      var node_view = new nodes.NodeView({model: node}),
          callback = sinon.spy(),
          // this would happen in renderShelf
          shelf = node_view.makeShelf();

      shelf.collection.add({});
      var shelf_item = shelf.list.at(0);

      shelf.on('foo', callback);
      assert.isFalse(callback.called);
      shelf_item.trigger('foo');
      assert.isTrue(callback.called);
    });
  });
});

describe('NodeView', function() {
  beforeEach(function() {
    test.create();

    root_node = {
      content: {
        preview_template: '<span><%author%><span>',
        component: 'testcomponent',
      },
      title: 'Test Title',
      author: 'Test Author',
    };

    this.node = new nodes.Node({
      content: {
        preview_template: '<span><%title%><span>',
        component: 'testcomponent',
      },
      title: 'Node Title',
      author: 'Node Author',
    });


    this.app_view = new widgy.AppView({ root_node: root_node });
  });

  afterEach(function() {
    test.destroy();
  });


  it('should return if it is the root node', function(done) {
    this.app_view.root_node_promise.then(function (root_node_view) {
      assert.isTrue(root_node_view.isRootNode());
      done();
    });
  });
});
