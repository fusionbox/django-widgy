var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var widgy = requirejs('widgy'),
    nodes = requirejs('nodes/nodes'),
    Backbone = requirejs('widgy.backbone'),
    sinon = requirejs('sinon'),
    Q = requirejs('lib/q'),
    $ = requirejs('jquery');

describe.skip('AppView', function() {
  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent'
      },
      title: 'Test Title',
      author: 'Test Author'
    });
  });

  it('should initialize an AppView', function() {
    return this.node.ready(function(node) {
      // getComponent is stubbed because testcomponent is inaccessable from AppView
      var deferal = {};
      _.extend(deferal, node); // copies node to prevent Backbone from making child
      var myAPI = function() { return Q(deferal); };
      sinon.stub(nodes.Node.prototype, 'getComponent', myAPI);

      var app_view = new widgy.AppView({root_node: node});

      nodes.Node.prototype.getComponent.restore();

      app_view.root_node_promise.then(function() {
        assert.strictEqual(app_view.node_view_list.at(0).content,
                            deferal.content);
      })
      .done();
    })
    .done();
  });

  it('should renderPromise', function() {
    return this.node.ready(function(node) {
      var deferal = {};
      _.extend(deferal, node);
      var myAPI = function() { return Q(deferal); };
      sinon.stub(nodes.Node.prototype, 'getComponent', myAPI);
      var app_view = new widgy.AppView({root_node: node, model: node});
      nodes.Node.prototype.getComponent.restore();


      app_view.root_node_promise.then(function() {
        app_view.root_node.available_children_url = '1';
        app_view.template = '<span><%title%></span>';

        // setup setCompatibility
        var root_view = app_view.node_view_list.at(0);
        root_view.content.shelf = true;
        root_view.shelf = root_view.makeShelf();

        // setup fetchCompatibility
        var testObject = [{model: {id: '1'}, __class__: '0'}];
        var myAPI = function() { return testObject; };
        sinon.stub($, 'ajax', myAPI);

        // stubbed to reduce complexity
        var templateAPI = function() { return '<div><%author%></div>'; }
        sinon.stub(root_view, 'getTemplate', templateAPI);

        test.create();

        var promise = app_view.renderPromise();

        promise.then(function() {
          assert.strictEqual(app_view.$el.html(), '<span>Test Title</span>');
          assert.strictEqual(root_view.$el.html(), '<div>Test Author</div>');
          assert.strictEqual(app_view.compatibility_data, testObject);
          test.destroy();
        });

        $.ajax.restore();
      })
      .done();
    })
    .done();
  });

  it('should fetchCompatibility', function() {
    return this.node.ready(function(node) {
      var deferal = {};
      _.extend(deferal, node);
      var myAPI = function() { return Q(deferal); };
      sinon.stub(nodes.Node.prototype, 'getComponent', myAPI);
      var app_view = new widgy.AppView({root_node: node});
      nodes.Node.prototype.getComponent.restore();

      app_view.root_node_promise.then(function() {
        var callback = sinon.spy();
        app_view.inflight = new Object({abort: callback});
        app_view.root_node.available_children_url = '1';

        var testObject = new Object();
        var myAPI = function() { return testObject; };
        sinon.stub($, 'ajax', myAPI);

        var promise = app_view.fetchCompatibility();

        $.ajax.restore();

        promise.then(function(inflight) {
          assert.strictEqual(inflight, testObject);
          assert.isTrue(callback.calledOnce);
        });
      })
      .done();
    })
    .done();
  });

  it('should refreshCompatibility', function() {
    return this.node.ready(function(node) {
      var deferal = {};
      _.extend(deferal, node);
      var myAPI = function() { return Q(deferal); };
      sinon.stub(nodes.Node.prototype, 'getComponent', myAPI);
      var app_view = new widgy.AppView({root_node: node});
      nodes.Node.prototype.getComponent.restore();

      app_view.root_node_promise.then(function() {
        app_view.root_node.available_children_url = '1';

        var root_view = app_view.node_view_list.at(0);
        root_view.content.shelf = true;
        root_view.shelf = root_view.makeShelf();

        var testObject = [{model: {id: '1'}, __class__: '0'}];
        var myAPI = function() { return testObject; };
        sinon.stub($, 'ajax', myAPI);

        var promise = Q(app_view.refreshCompatibility());

        $.ajax.restore();

        promise.then(function() {
          assert.strictEqual(app_view.compatibility_data, testObject);
        });
      })
      .done();
    })
    .done();
  });

  it('should setCompatibility and updateCompatibility', function() {
    return this.node.ready(function(node) {
      var deferal = {};
      _.extend(deferal, node);
      var myAPI = function() { return Q(deferal); };
      sinon.stub(nodes.Node.prototype, 'getComponent', myAPI);
      var app_view = new widgy.AppView({root_node: node});
      nodes.Node.prototype.getComponent.restore();

      app_view.root_node_promise.then(function() {
        var data = [{model: {id: '1'}, __class__: '0'}];
        var root_view = app_view.node_view_list.at(0);
        root_view.content.shelf = true;
        root_view.shelf = root_view.makeShelf();

        var callback_add = sinon.spy(root_view.shelf, 'addOptions');
        var callback_filter = sinon.spy(root_view.shelf, 'filterDuplicates');

        app_view.setCompatibility(data);
        assert.strictEqual(app_view.compatibility_data, data);
        assert.isTrue(callback_add.calledOnce);
        assert.isTrue(callback_filter.calledOnce);

        callback_add.restore();
        callback_filter.restore();
      })
      .done();
    })
    .done();
  });

  it('should return if ready or not', function() {
    return this.node.ready(function(node) {
      var deferal = {};
      _.extend(deferal, node);
      var myAPI = function() { return Q(deferal); };
      sinon.stub(nodes.Node.prototype, 'getComponent', myAPI);
      var app_view = new widgy.AppView({root_node: node});
      nodes.Node.prototype.getComponent.restore();

      app_view.root_node_promise.then(function() {
        assert.isFalse(app_view.ready());

        var data = [{model: {id: '1'}, __class__: '0'}];
        var root_view = app_view.node_view_list.at(0);
        root_view.content.shelf = true;
        root_view.shelf = root_view.makeShelf();
        app_view.setCompatibility(data);

        assert.isTrue(app_view.ready());
      })
      .done();
    })
    .done();
  });
});
