var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert,
    sinon = require('sinon');

var nodes = requirejs('nodes/nodes'),
    DraggableView = requirejs('nodes/base'),
    widgy = requirejs('widgy'),
    shelves = requirejs('shelves/shelves'),
    _ = requirejs('underscore'),
    Q = requirejs('lib/q');

describe('DraggablewView', function() {
  var TestView = DraggableView.extend({
    initialize: function() {
      DraggableView.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'test_render'
      );
    },
    test_render: function() {
      DraggableView.prototype.render.apply(this, arguments);
    }
  });

  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent'
      },
      css_classes: {'foo': 'bar'}
    });
  });

  it('should render', function() {
    return this.node.ready(function(node) {
      var test_view = new TestView({model: node});
      test_view.test_render();
      assert.isTrue(test_view.$el.hasClass('bar'));
    });
  });
});
