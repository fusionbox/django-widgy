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
        component: 'testcomponent',
        preview_template: '<span><%preview_template%></span>'
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
        var parent_view = app_view.node_view_list.at(0);
        parent_view.$preview = parent_view.$(' > .widget > .preview ');
        parent_view.$children = parent_view.$(' > .widget > .node_chidren ');

        var templateAPI = function() {
          return Q('<span><%title%></span>').then(function() {
            node_array[1].component.View.prototype.renderPromise.restore();
            parent_view.startDrag(app_view.node_view_list.at(1));

            var drop_targets_list = parent_view.drop_targets_list;

            assert.strictEqual(parent_view.dragged_view, app_view.node_view_list.at(1));
            assert.instanceOf(drop_targets_list.at(0), nodes.DropTargetView);
            assert.isTrue(drop_targets_list.at(0).$el.hasClass('previous'));
            assert.isTrue(drop_targets_list.at(0).$el.hasClass('active'));
            assert.isFalse(drop_targets_list.at(1).$el.hasClass('previous'));
            assert.deepEqual(drop_targets_list.at(1).$el.css('display'), 'none');

            // Could be seperate test - Tests DropTargetView.deactivate
            drop_targets_list.at(0).deactivate('');
            assert.isFalse(drop_targets_list.at(0).$el.hasClass('active'));

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

  it('should stopDrag', function() {
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
        var parent_view = app_view.node_view_list.at(0);
        parent_view.shelf = parent_view.makeShelf();
        parent_view.$preview = parent_view.$(' > .widget > .preview ');
        parent_view.$children = parent_view.$(' > .widget > .node_chidren ');

        var templateAPI = function() {
          return Q('<span><%title%></span>').then(function() {
            node_array[1].component.View.prototype.renderPromise.restore();
            parent_view.startDrag(app_view.node_view_list.at(1));
            assert.strictEqual(parent_view.dragged_view, app_view.node_view_list.at(1));
            assert.isNotNull(parent_view.drop_targets_list.at(0));

            var callback = sinon.spy();

            parent_view.stopDrag(callback);

            assert.isTrue(callback.calledWith(app_view.node_view_list.at(1)));
            assert.isUndefined(parent_view.dragged_view);
            assert.isUndefined(parent_view.drop_targets_list.at(0));
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

  it('should getTemplate', function() {
    return this.node.ready(function(node) {
      var node_view = new nodes.NodeView({model: node});
      assert.deepEqual(node_view.getTemplate(), '<span><%preview_template%></span>');
    });
  });

  it('should cleanUp', function() {
    return this.node.ready(function(node) {
      var node_view = new nodes.NodeView({model: node});
      node_view.shelf = node_view.makeShelf();
      node_view.$preview = node_view.$(' > .widget > .preview ');
      node_view.$children = node_view.$(' > .widget > .node_chidren ');
      node_view.cleanUp();
    });
  });

  it('should popOut', function() {
    return this.node.ready(function(node) {
      var node_view = new nodes.NodeView({model: node});
      node_view.shelf = node_view.makeShelf();
      node_view.$preview = node_view.$(' > .widget > .preview ');
      node_view.$children = node_view.$(' > .widget > .node_chidren ');
      var eve = $.Event('click', {target: {href: {foo: 'bar'}}});
      sinon.stub(window, 'open', function(val) {return val;});

      node_view.popOut(eve);

      window.open.restore();

      assert.strictEqual(node_view.subwindow.widgyCloseCallback, node_view.popIn);
      assert.isTrue(node_view.$el.hasClass('poppedOut'));
    });
  });

  it('should popIn', function() {
    return this.node.ready(function(node) {
      var node_view = new nodes.NodeView({model: node});
      node_view.shelf = node_view.makeShelf();
      node_view.$preview = node_view.$(' > .widget > .preview ');
      node_view.$children = node_view.$(' > .widget > .node_chidren ');
      var eve = $.Event('click', {target: {href: {foo: 'bar'}}});
      sinon.stub(window, 'open', function(val) {return val;});
      sinon.stub(node_view.node, 'fetch', function() {return;}); // stops rerender

      node_view.popOut(eve);
      node_view.popIn(eve);

      window.open.restore();
      node_view.node.fetch.restore();

      assert.isFalse(node_view.$el.hasClass('poppedOut'));
    });
  });

  it('should closeSubwindow', function() {
    return this.node.ready(function(node) {
      var node_view = new nodes.NodeView({model: node});
      node_view.shelf = node_view.makeShelf();
      node_view.$preview = node_view.$(' > .widget > .preview ');
      node_view.$children = node_view.$(' > .widget > .node_chidren ');
      var callback = sinon.spy();
      var eve = $.Event('click', {target: {href: {foo: 'bar', close: callback}}});
      sinon.stub(window, 'open', function(val) {return val;});

      node_view.popOut(eve);
      assert.isFalse(node_view.closeSubwindow());

      window.open.restore();

      assert.isTrue(callback.calledOnce);
    });
  });
});
