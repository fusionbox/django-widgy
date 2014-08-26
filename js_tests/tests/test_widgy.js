var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var widgy = requirejs('widgy'),
    nodes = requirejs('nodes/nodes'),
    Backbone = requirejs('widgy.backbone'),
    sinon = requirejs('sinon'),
    Q = requirejs('lib/q'),
    $ = requirejs('jquery');


describe('AppView', function() {
  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent'
      },
      title: 'Test Title',
      author: 'Test Author'
    });

    this.root_node = {
      content: {
        component: 'testcomponent'
      },
      title: 'Test Title',
      author: 'Test Author',
    };
  });


  it('should initialize an AppView', function(done) {
    var app_view = new widgy.AppView({ root_node: this.root_node });
    app_view.root_node_promise.then(function(root_node_view) {
      assert.equal(root_node_view.model.attributes.title, 'Test Title');
      done();
    });
  });


  it('should renderPromise', function(done) {
    var app_view = new widgy.AppView({ root_node: this.root_node });
    app_view.root_node_promise.then(function() {
      /*app_view.root_node.available_children_url = '1';
      app_view.template = '<span><%title%></span>';

      // setup setCompatibility
      var root_view = app_view.node_view_list.at(0);
      root_view.content.shelf = true;
      root_view.shelf = root_view.makeShelf();

      // setup fetchCompatibility
      var testObject = [{ model: { id: '1' }, __class__: '0' }];
      sinon.stub($, 'ajax', function() { return testObject; });

      // stubbed to reduce complexity
      var getTemplateStub = sinon.stub(root_view, 'getTemplate', function()
                                       { return '<div><%author%></div>'; });
      var makeStickyStub = sinon.stub(root_view, 'makeSticky',
                                      function () { return });
*/
      test.create();

      app_view.renderPromise().then(function() {
        assert.strictEqual(app_view.$el.html(), '<span>Test Title</span>');
        assert.strictEqual(root_view.$el.html(), '<div>Test Author</div>');
        assert.strictEqual(app_view.compatibility_data, testObject);
        test.destroy();
        getComponentStub.restore();
        getTemplateStub.restore();
        makeStickyStub.restore();
        $.ajax.restore();
        done();
      });
    });
  });


  it('should fetchCompatibility', function(done) {
    return this.node.ready(function(node) {
      var node_object = {};
      _.extend(node_object, node);
      var getComponentStub = sinon.stub(nodes.Node.prototype, 'getComponent',
                                        function() { return Q(node_object); });
      var app_view = new widgy.AppView({ root_node: node });

      app_view.root_node_promise.then(function() {
        var callback = sinon.spy();
        app_view.inflight = new Object({ abort: callback });
        app_view.root_node.available_children_url = '1';

        var testObject = new Object();
        sinon.stub($, 'ajax', function() { return testObject; });

        var promise = app_view.fetchCompatibility();

        promise.then(function(inflight) {
          assert.strictEqual(inflight, testObject);
          assert.isTrue(callback.calledOnce);
          getComponentStub.restore();
          $.ajax.restore();
          done();
        });
      });
    });
  });


  it('should refreshCompatibility', function(done) {
    return this.node.ready(function(node) {
      var node_object = {};
      _.extend(node_object, node);
      var getComponentStub = sinon.stub(nodes.Node.prototype, 'getComponent',
                                        function() { return Q(node_object); });
      var app_view = new widgy.AppView({ root_node: node });

      app_view.root_node_promise.then(function() {
        app_view.root_node.available_children_url = '1';

        var root_view = app_view.node_view_list.at(0);
        root_view.content.shelf = true;
        root_view.shelf = root_view.makeShelf();

        var testObject = [{ model: { id: '1' }, __class__: '0' }];
        sinon.stub($, 'ajax', function() { return testObject; });

        var promise = Q(app_view.refreshCompatibility());

        promise.then(function() {
          assert.strictEqual(app_view.compatibility_data, testObject);
          getComponentStub.restore();
          $.ajax.restore();
          done();
        });
      });
    });
  });


  it('should setCompatibility and updateCompatibility', function(done) {
    return this.node.ready(function(node) {
      var node_object = {};
      _.extend(node_object, node);
      var getComponentStub = sinon.stub(nodes.Node.prototype, 'getComponent',
                                        function() { return Q(node_object); });
      var app_view = new widgy.AppView({ root_node: node });

      app_view.root_node_promise.then(function() {
        var data = [{ model: { id: '1' }, __class__: '0' }];
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
        getComponentStub.restore();
        done();
      });
    });
  });


  it('should return if ready or not', function(done) {
    return this.node.ready(function(node) {
      var node_object = {};
      _.extend(node_object, node);
      var getComponentStub = sinon.stub(nodes.Node.prototype, 'getComponent',
                                        function() { return Q(node_object); });
      var app_view = new widgy.AppView({ root_node: node });

      app_view.root_node_promise.then(function() {
        assert.isFalse(app_view.ready());

        var data = [{ model: { id: '1' }, __class__: '0' }];
        var root_view = app_view.node_view_list.at(0);
        root_view.content.shelf = true;
        root_view.shelf = root_view.makeShelf();
        app_view.setCompatibility(data);

        assert.isTrue(app_view.ready());
        getComponentStub.restore();
        done();
      });
    });
  });
});
