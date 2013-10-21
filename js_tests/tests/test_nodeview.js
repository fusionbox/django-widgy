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

describe('CoreFunctions', function() {
  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent'
      }
    });

    this.node2 = new nodes.Node({
      content: {
        component: 'testcomponent'
      }
    });
  });

  it('should return if it is the root node', function() {
    var nodes_promise = Q.all([this.node.ready(), this.node2.ready()]);
    nodes_promise.then(function(node_array) {
      var deferal = {};
      _.extend(deferal, node_array[0]);
      var myAPI = function() { return Q(deferal); };
      sinon.stub(nodes.Node.prototype, 'getComponent', myAPI);
      var app_view = new widgy.AppView({root_node: node_array[0], model: node_array[0]});
      nodes.Node.prototype.getComponent.restore();

      app_view.root_node_promise.then(function() {
        node_array[1].component.View.prototype.title = 'Root Node';

        var parent_view = app_view.node_view_list.at(0);
        parent_view.$preview = parent_view.$(' > .widget > .preview ');
        parent_view.$children = parent_view.$(' > .widget > .node_chidren ');

        var templateAPI = function() {
          return Q('<span><%title%></span>').then(function() {
            assert.isFalse(app_view.node_view_list.at(1).isRootNode());
            node_array[1].component.View.prototype.renderPromise.restore();
          });
        }
        sinon.stub(node_array[1].component.View.prototype, 'renderPromise', templateAPI);

        deferal.children.add(node_array[1]);

        assert.isTrue(parent_view.isRootNode());

      })
      .done();
    })
    .done();
  });

  it('should deleteSelf', function() {
    return this.node.ready(function(node) {
      var node_view = new nodes.NodeView({model: node});
      node_view.shelf = node_view.makeShelf();
      node_view.node.collection = node.children;

      sinon.spy(node_view.node, 'destroy');
      sinon.spy(node_view.list, 'closeAll');
      sinon.spy(node_view.shelf, 'close');

      node_view.deleteSelf();

      assert.isTrue(node_view.node.destroy.calledOnce);
      assert.isTrue(node_view.list.closeAll.calledOnce);
      assert.isTrue(node_view.shelf.close.calledOnce);

      node_view.node.destroy.restore();
      node_view.list.closeAll.restore();
      node_view.shelf.close.restore();
    })
    .done();
  });

  it('should startDrag', function() {
    test.create();
    var nodes_promise = Q.all([this.node.ready(), this.node2.ready()]);
    nodes_promise.then(function(node_array) {
      var deferal = {};
      _.extend(deferal, node_array[0]);
      var myAPI = function() { return Q(deferal); };
      sinon.stub(nodes.Node.prototype, 'getComponent', myAPI);
      var app_view = new widgy.AppView({root_node: node_array[0], model: node_array[0]});
      nodes.Node.prototype.getComponent.restore();

      app_view.root_node_promise.then(function() {
        node_array[1].component.View.prototype.title = 'Root Node';

        var parent_view = app_view.node_view_list.at(0);
        parent_view.$preview = parent_view.$(' > .widget > .preview ');
        parent_view.$children = parent_view.$(' > .widget > .node_chidren ');

        var draggable_view = new nodes.NodeView({model: node_array[1]});

        var templateAPI = function() {
          return Q('<span><%title%></span>').then(function() {
            node_array[1].component.View.prototype.renderPromise.restore();
            app_view.node_view_list.at(0).startDrag(app_view.node_view_list.at(1));

            var drop_targets_list = app_view.node_view_list.at(0).drop_targets_list;

            assert.instanceOf(drop_targets_list.at(0), nodes.DropTargetView);
            assert.isTrue(drop_targets_list.at(0).$el.hasClass('previous'));
            assert.isFalse(drop_targets_list.at(1).$el.hasClass('previous'));
            assert.deepEqual(drop_targets_list.at(1).$el.css('display'), 'none');
            test.destroy();
          });
        }
        sinon.stub(node_array[1].component.View.prototype, 'renderPromise', templateAPI);

        deferal.children.add(node_array[1]);
      })
      .done();
    })
    .done();
  });
});
