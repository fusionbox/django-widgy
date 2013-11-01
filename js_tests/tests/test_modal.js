var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var modal = requirejs('modal/modal'),
    sinon = requirejs('sinon'),
    $ = requirejs('jquery');

describe('ModalView', function() {
  it('should return the message with toJSON', function() {
    var modal_view = new modal.ModalView();
    modal_view.message = 'Test Complete';
    assert.deepEqual(modal_view.toJSON(), {message: 'Test Complete'});
  });

  it('should open a window', function() {
    test.create();
    var modal_view = new modal.ModalView();
    modal_view.open();
    assert.isTrue($('div:[1]').hasClass('modal'));
    assert.deepEqual($('div').css('position'), 'fixed');
    $(document.body).children().remove();
    test.destroy();
  });
});

describe('ErrorView', function() {
  it('should construct a new ErrorView', function() {
    var error_view = new modal.ErrorView({message: 'Test Message'});
    assert.deepEqual(error_view.message, 'Test Message');
  });
});

describe('Modal Static Functions', function() {
  beforeEach(function() {
    test.create();
  });

  afterEach(function() {
    test.destroy();
  });

  it('should raiseError', function() {
    test.create();
    modal.raiseError('Test Message');
    assert.isTrue($('div:[1]').hasClass('modal'));
    assert.deepEqual($('div').css('position'), 'fixed');
    assert.deepEqual($('.serverResponse').html(), 'Test Message');
    $(document.body).children().remove();
  });

  it('should handle an ajaxError', function() {
    var model = new Object(),
        resp = {
          getResponseHeader: function() {return ['application/json'];},
          responseText: '"Data Test"',
          status: 200
        },
        options = {};

    modal.ajaxError(model, resp, options);
    assert.deepEqual($('.serverResponse').html(), 'Data Test');
    $(document.body).children().remove();

    resp.responseText = new Object('{"message": "Object Test"}');
    modal.ajaxError(model, resp, options);
    assert.deepEqual($('.serverResponse').html(), 'Object Test');
    $(document.body).children().remove();

    resp.responseText = '{}';
    modal.ajaxError(model, resp, options);
    assert.deepEqual($('.serverResponse').html(), 'Unknown error');
    $(document.body).children().remove();

    resp.status = 404;
    modal.ajaxError(model, resp, options);
    assert.deepEqual($('.serverResponse').html(), 'Try refreshing the page');
    $(document.body).children().remove();
  });

  it('should handle an ajaxError with a non-json response', function(){
    var model = new Object(),
        resp = {
          getResponseHeader: function() {return ['app/not/json'];},
          responseText: 'Test Failure'
        },
        options = {};
    modal.ajaxError(model, resp, options);
    assert.deepEqual($('.serverResponse').html(), 'Test Failure');
    $(document.body).children().remove();
  });

  it('should confirm success', function() {
    var message = 'Are you sure you want to delete?',
        success = sinon.spy(),
        failure = sinon.spy(),
        stub = sinon.stub(window, 'confirm').returns(true);
    modal.confirm(message, success, failure);
    assert.isTrue(stub.calledOnce);
    assert.isTrue(success.calledOnce);
    assert.isFalse(failure.calledOnce);
    stub.restore();
  });

  it('should confirm failure', function() {
    var message = 'Are you sure you want to delete?',
        success = sinon.spy(),
        failure = sinon.spy(),
        stub = sinon.stub(window, 'confirm').returns(false);
    modal.confirm(message, success, failure);
    assert.isTrue(stub.calledOnce);
    assert.isFalse(success.calledOnce);
    assert.isTrue(failure.calledOnce);
    stub.restore();
  });
});
