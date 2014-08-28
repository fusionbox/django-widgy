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
    test.create();

    this.root_node = {
      content: {
        preview_template: '<span><%author%><span>',
        component: 'testcomponent',
      },
      title: 'Test Title',
      author: 'Test Author',
    };
  });

  afterEach(function() {
    test.destroy();
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
      var testObject = [{ model: { id: '1' }, __class__: '0' }];
      sinon.stub($, 'ajax', function() { return testObject; });

      app_view.renderPromise().then(function() {
        assert.strictEqual(app_view.compatibility_data, testObject);
        $.ajax.restore();
        done();
      });
    });
  });


  it('should fetchCompatibility', function(done) {
    var app_view = new widgy.AppView({ root_node: this.root_node });

    app_view.root_node_promise.then(function() {
      var callback = sinon.spy();
      app_view.inflight = new Object({ abort: callback });

      var testObject = new Object();
      sinon.stub($, 'ajax', function() { return testObject; });

      var promise = app_view.fetchCompatibility();

      promise.then(function(inflight) {
        assert.strictEqual(inflight, testObject);
        assert.isTrue(callback.calledOnce);
        $.ajax.restore();
        done();
      });
    });
  });


  it('should refreshCompatibility', function(done) {
    var app_view = new widgy.AppView({ root_node: this.root_node });

    app_view.root_node_promise.then(function() {

      var testObject = [{ model: { id: '1' }, __class__: '0' }];
      sinon.stub($, 'ajax', function() { return testObject; });

      var promise = Q(app_view.refreshCompatibility());

      promise.then(function() {
        assert.strictEqual(app_view.compatibility_data, testObject);
        $.ajax.restore();
        done();
      });
    });
  });


  it('should setCompatibility and updateCompatibility', function(done) {
    var app_view = new widgy.AppView({ root_node: this.root_node });

    app_view.root_node_promise.then(function(root_node_view) {
      var data = {};
      data[root_node_view.node.id] =  [
        {
          'css_classes': ['foo', 'bar'],
          '__class__': 'class',
          'tooltip': null,
          'title': 'Tip'
        }
      ];

      app_view.setCompatibility(data);
      done();
    });
  });

  it('should know what objects are compatibale', function(done) {
    var app_view = new widgy.AppView({ root_node: this.root_node });

    app_view.root_node_promise.then(function(root_node_view) {
      var data = {};
      data[root_node_view.node.id] =  [
        {
          'css_classes': ['foo', 'bar'],
          '__class__': 'class',
          'tooltip': null,
          'title': 'Tip'
        }
      ];

      app_view.setCompatibility(data);
      done();
    });
  });

  it('should return if ready or not', function(done) {
    var app_view = new widgy.AppView({ root_node: this.root_node });

    app_view.root_node_promise.then(function(root_node_view) {
      assert.isFalse(app_view.ready());

      var data = {};
      data[root_node_view.node.id] =  [
        {
          'css_classes': ['foo', 'bar'],
          '__class__': 'class',
          'tooltip': null,
          'title': 'Tip'
        }
      ];
      app_view.setCompatibility(data);

      assert.isTrue(app_view.ready());
      done();
    });
  });
});
