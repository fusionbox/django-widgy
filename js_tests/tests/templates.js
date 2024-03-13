var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var templates = requirejs('templates'),
    Backbone = requirejs('widgy.backbone'),
    sinon = requirejs('sinon'),
    Q = requirejs('lib/q'),
    $ = requirejs('jquery');

describe('getTemplate', function() {

  // AJAX/Promise strategy from  http://martinfowler.com/articles/asyncJS.html

  it('should getTemplate', function(done) {
    var simulatedAjaxResponse = {
      template: '<span><%title%></span>'
    };
    var stub = sinon.stub($, 'ajax', function() { return Q(simulatedAjaxResponse); });
    templates.getTemplate('1').then(function(template) {
      assert.equal(template.get('template'), simulatedAjaxResponse['template']);
      stub.restore();
      done();
    });
  });
});
