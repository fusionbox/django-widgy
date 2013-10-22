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
        'funcToTest'
      );
    },
    funcToTest: function() {
      DraggableView.prototype.render.apply(this, arguments);
    },

    canAcceptParent: function() {
      return true;
    },

    cssClasses: function() {
      return {};
    }
  });

  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent',
      }
    });
  });

  it('should initialize a DraggablewView', function() {
    return this.node.ready(function(node) {
      var test_view = new TestView({model: node});
      test_view.funcToTest();
    });
  });
});
