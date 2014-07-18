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
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent',
        preview_template: '<span>preview_template</span>'
      }
    });

    this.node2 = new nodes.Node({
      content: {
        component: 'testcomponent'
      }
    });
  });

  describe('as root node', function() {
    var root_node_setup;
    beforeEach(function(done) {
      var nodes_promise = Q.all([this.node.ready(), this.node2.ready()]);
      root_node_setup =  nodes_promise.then(function(node_array) {
        var node_object = {};
        _.extend(node_object, node_array[0]);
        var getComponentStub = sinon.stub(nodes.Node.prototype, 'getComponent',
                                      function() { return Q(node_object); });
        var app_view = new widgy.AppView({
          root_node: node_array[0],
          model: node_array[0]
        });
        return {
          node_object: node_object,
          node_array: node_array,
          app_view: app_view,
          getComponentStub: getComponentStub,
        };
      });
      done();
    });

    it('should return if it is the root node', function(done) {
      root_node_setup.then(function (app_view_object) {
        app_view_object.app_view.root_node_promise.then(function(parent_view) {
          parent_view.$preview = parent_view.$(' > .widget > .preview ');
          parent_view.$children = parent_view.$(' > .widget > .node_chidren ');

          var templateAPI = function() {
            return Q('<span><%title%></span>').then(function() {
              assert.isFalse(app_view_object.app_view.node_view_list.at(1).isRootNode());
              nodeArrayStub.restore();
              app_view_object.getComponentStub.restore();
              done();
            });
          }

          var nodeArrayStub = sinon.stub(app_view_object.node_array[1].component.View.prototype,
                                        'renderPromise', templateAPI);

          app_view_object.node_object.children.add(app_view_object.node_array[1]);

          assert.isTrue(parent_view.isRootNode());
        });
      });
    });

    it('should create drop targets with startDrag', function(done) {
      test.create();
      root_node_setup.then(function (app_view_object) {
        app_view_object.app_view.root_node_promise.then(function(parent_view) {
          parent_view.$preview = parent_view.$(' > .widget > .preview ');
          parent_view.$children = parent_view.$(' > .widget > .node_chidren ');

          var templateAPI = function() {
            return Q('<span><%title%></span>').then(function() {
              var drop_targets_spy = sinon.spy(parent_view, 'addDropTargets');
              var accept_child_spy = sinon.spy(parent_view, 'canAcceptChild');
              parent_view.startDrag(app_view_object.app_view.node_view_list.at(1));

              assert.strictEqual(parent_view.dragged_view, app_view_object.app_view.node_view_list.at(1));

              var dragged_view = parent_view.dragged_view;
              assert.isTrue(drop_targets_spy.withArgs(dragged_view).calledOnce);
              assert.isTrue(accept_child_spy.withArgs(dragged_view).calledOnce);
              assert.isTrue(accept_child_spy.withArgs(dragged_view).returned(true));
              drop_targets_spy.restore();
              accept_child_spy.restore();

              var drop_targets_list = parent_view.drop_targets_list;
              assert.instanceOf(drop_targets_list.at(0), nodes.DropTargetView);
              assert.isTrue(drop_targets_list.at(0).$el.hasClass('previous'));
              assert.isTrue(drop_targets_list.at(0).$el.hasClass('active'));
              assert.isFalse(drop_targets_list.at(1).$el.hasClass('previous'));
              assert.deepEqual(drop_targets_list.at(1).$el.css('display'), 'none');

              // Could be seperate test - Tests DropTargetView.deactivate
              drop_targets_list.at(0).deactivate('');
              assert.isFalse(drop_targets_list.at(0).$el.hasClass('active'));

              test.destroy();
              app_view_object.getComponentStub.restore();
              nodeArrayStub.restore();
              done();
            });
          }
          var nodeArrayStub = sinon.stub(app_view_object.node_array[1].component.View.prototype, 'renderPromise', templateAPI);

          app_view_object.node_object.children.add(app_view_object.node_array[1]);
        });
      });
    });

    it('should remove drop targets with stopDrag', function(done) {
      test.create();
      root_node_setup.then(function(app_view_object) {
        app_view_object.app_view.root_node_promise.then(function(parent_view) {
          var parent_view = app_view_object.app_view.node_view_list.at(0);
          parent_view.shelf = parent_view.makeShelf();
          parent_view.$preview = parent_view.$(' > .widget > .preview ');
          parent_view.$children = parent_view.$(' > .widget > .node_chidren ');

          var templateAPI = function() {
            return Q('<span><%title%></span>').then(function() {
              nodeArrayStub.restore();
              parent_view.startDrag(app_view_object.app_view.node_view_list.at(1));
              assert.isNotNull(parent_view.drop_targets_list.at(0));

              var callback = sinon.spy();
              parent_view.stopDrag(callback);

              assert.isTrue(callback.calledWith(app_view_object.app_view.node_view_list.at(1)));
              assert.isUndefined(parent_view.dragged_view);
              assert.isUndefined(parent_view.drop_targets_list.at(0));

              app_view_object.getComponentStub.restore();
              test.destroy();
              done();
            });
          }
          var nodeArrayStub = sinon.stub(app_view_object.node_array[1].component.View.prototype, 'renderPromise', templateAPI);

          app_view_object.node_object.children.add(app_view_object.node_array[1]);
        });
      });
    });
  });

  describe('core functions', function() {
    var create_node_view = function(node) {
      var node_view = new nodes.NodeView({model: node});
      node_view.shelf = node_view.makeShelf();
      node_view.$preview = node_view.$(' > .widget > .preview ');
      node_view.$children = node_view.$(' > .widget > .node_chidren ');
      node_view.node.collection = node.children;
      return node_view;
    };

    it('should getTemplate', function(done) {
      return this.node.ready(function(node) {
        var node_view = new nodes.NodeView({model: node});
        assert.deepEqual(node_view.getTemplate(), '<span>preview_template</span>');
        done();
      });
    });

    it('should deleteSelf', function(done) {
      return this.node.ready(function(node) {
        var node_view = create_node_view(node);

        sinon.spy(node_view.node, 'destroy');
        sinon.spy(node_view.list, 'closeAll');
        sinon.spy(node_view.shelf, 'close');

        node_view.deleteSelf();

        assert.isTrue(node_view.node.destroy.calledOnce);
        assert.isTrue(node_view.list.closeAll.calledOnce);
        assert.isTrue(node_view.shelf.close.calledTwice);

        node_view.node.destroy.restore();
        node_view.list.closeAll.restore();
        node_view.shelf.close.restore();
        done();
      });
    });

    it('should popOut', function(done) {
      return this.node.ready(function(node) {
        var node_view = create_node_view(node);
        var eve = $.Event('click', {target: {href: {foo: 'bar'}}});
        sinon.stub(window, 'open', function(val) {return val;});

        node_view.popOut(eve);

        window.open.restore();

        assert.strictEqual(node_view.subwindow.widgyCloseCallback, node_view.popIn);
        assert.isTrue(node_view.$el.hasClass('poppedOut'));
        done();
      });
    });

    it('should popIn', function(done) {
      return this.node.ready(function(node) {
        var node_view = create_node_view(node);
        var eve = $.Event('click', {target: {href: {foo: 'bar'}}});
        sinon.stub(window, 'open', function(val) {return val;});
        sinon.stub(node_view.node, 'fetch', function() {return;}); // stops rerender

        node_view.popOut(eve);
        node_view.popIn(eve);

        window.open.restore();
        node_view.node.fetch.restore();

        assert.isFalse(node_view.$el.hasClass('poppedOut'));
        done();
      });
    });

    it('should closeSubwindow', function(done) {
      return this.node.ready(function(node) {
        var node_view = create_node_view(node);
        var callback = sinon.spy();
        var eve = $.Event('click', {target: {href: {foo: 'bar', close: callback}}});
        sinon.stub(window, 'open', function(val) {return val;});

        node_view.popOut(eve);
        assert.isFalse(node_view.closeSubwindow());

        window.open.restore();

        assert.isTrue(callback.calledOnce);
        done();
      });
    });

  });
});
