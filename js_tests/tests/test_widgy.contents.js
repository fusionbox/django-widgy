var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var nodes = requirejs('nodes/nodes')
    Backbone = requirejs('widgy.backbone'),
    contents = requirejs('widgy.contents'),
    $ = requirejs('jquery'),
    Q = requirejs('lib/q'),
    sinon = requirejs('sinon');

describe('Content', function() {
  it('should check if editable - false', function(done) {
    var node = new nodes.Node({
      content: {
        component: 'testcomponent',
      }
    });
    return node.ready(function() {
      assert.isFalse(node.content.isEditable());
      done();
    })
  });

  it('should check if editable - true', function(done) {
    var node = new nodes.Node({
      content: {
        component: 'testcomponent',
        edit_url: 'testurl'
      }
    });
    return node.ready(function() {
      assert.isTrue(node.content.isEditable());
      done();
    })
  });
});
