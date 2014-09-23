var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var modal = requirejs('modal/modal'),
    sinon = requirejs('sinon'),
    $ = requirejs('jquery');

describe('ModalView', function() {
  it('should open a window', function() {
    test.create();
    var modal_view = new modal.ModalView();
    assert.equal($('div.modal').length, 0);
    modal_view.open();
    assert.equal($('div.modal').length, 1);
    $(document.body).children().remove();
    test.destroy();
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
    assert.equal($('div.modal').length, 0);
    modal.raiseError('Test Message');
    assert.equal($('div.modal').length, 1);
    assert.equal($('.serverResponse').html(), 'Test Message');
  });


  describe('should handle an ajaxError', function() {
    beforeEach(function() {
      this.model = {};
      this.resp = {
            getResponseHeader: function() { return ['application/json']; },
            responseText: '"Data Test"',
            status: 200
          };
      this.options = {};
    });

    it('with responseText', function() {
      modal.ajaxError(this.model, this.resp, this.options);
      assert.equal($('.serverResponse').html(), 'Data Test');
    });

    it('with responseText Object', function() {
      this.resp.responseText = '{ "message": "Object Test" }';
      modal.ajaxError(this.model, this.resp, this.options);
      assert.equal($('.serverResponse').html(), 'Object Test');
    });

    it('with undefined responseText', function() {
      this.resp.responseText = '{}';
      modal.ajaxError(this.model, this.resp, this.options);
      assert.equal($('.serverResponse').html(), 'Unknown error');
    });

    it('with 404 status', function() {
      this.resp.status = 404;
      modal.ajaxError(this.model, this.resp, this.options);
      assert.equal($('.serverResponse').html(), 'Try refreshing the page');
    });

    it("does not explode with a non-json response", function() {
      this.resp.getResponseHeader = function() { return ['app/not/json']; };
      modal.ajaxError(this.model, this.resp, this.options);
      assert.equal($('.serverResponse').html(), '"Data Test"');
    });
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
