var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert,
    sinon = require('sinon');

var nodes = requirejs('nodes/nodes'),
    DraggableView = requirejs('nodes/base'),
    _ = requirejs('underscore');

describe('DraggablewView', function() {
  var TestView = DraggableView.extend({
    initialize: function() {
      DraggableView.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'testRender',
        'testCssClasses'
      );
    },

    testRender: function() {
      DraggableView.prototype.render.apply(this, arguments);
    },

    testRenderPromise: function() {
      DraggableView.prototype.renderPromise.apply(this, arguments);
    },

    testCssClasses: function() {
      return DraggableView.prototype.cssClasses.apply(this, arguments);
    }
  });


  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent'
      },
      css_classes: [ 'foo', 'bar' ]
    });
  });


  it('should render', function(done) {
    return this.node.ready(function(node) {
      var test_view = new TestView({ model: node });
      test_view.testRender();
      assert.isTrue(test_view.$el.hasClass('bar'));
      done();
    });
  });

  it('should return cssClasses', function(done) {
    return this.node.ready(function(node) {
      var test_view = new TestView({ model: node });
      assert.deepEqual(test_view.testCssClasses(), [ 'foo', 'bar' ]);
      done();
    });
  });
});
