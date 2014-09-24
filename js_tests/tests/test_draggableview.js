var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var nodes = requirejs('nodes/nodes'),
    DraggableView = requirejs('nodes/base'),
    _ = requirejs('underscore');

describe('DraggableView', function() {
  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent'
      },
      css_classes: [ 'foo', 'bar' ]
    });
  });


  it('adds css_classes when rendered', function(done) {
    return this.node.ready(function(node) {
      var test_view = new DraggableView({ model: node });
      test_view.renderPromise().then(function(view) {
        assert.isTrue(view.$el.hasClass('bar'));
        done();
      });
    });
  });
});
