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
    var compareModel = new Backbone.Model({
      url: '1',
      template: '<span><%title%></span>'
    });
    var simulatedAjaxResponse = {
      template: '<span><%title%></span>'
    };
    var stub = sinon.stub($, 'ajax', function() { return Q(simulatedAjaxResponse); });
    var templatePromise = templates.getTemplate('1');

    templatePromise.then(function(temp) {
      assert.deepEqual(temp.attributes, compareModel.attributes);
      assert.strictEqual(temp.render('template', {title: 'test'}), '<span>test</span>');
      stub.restore();
      done();
    });
  });
});
