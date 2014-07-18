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

describe('EditorView', function() {
  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent',
        template_url: '1',
        url: '1',
        form_prefix: 'ev'
      }
    });
  });

  it('should return template', function(done) {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
            'model': node.content
          });
      var simulated_ajax_response = {
        template: '<span><%title%></span>',
        edit_template: '<span><%edit_template%></span>'
      };
      var stub = sinon.stub($, 'ajax',
        function() { return Q(simulated_ajax_response); });
      var template_promise = edit_view.getTemplate();

      template_promise.then(function(temp) {
        assert.deepEqual(temp, '<span><%edit_template%></span>');
        $.ajax.restore();
        done();
      })
    })
  });

  it('should submit and call serialize', function(done) {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
            'model': node.content
          });
      sinon.spy(edit_view, 'serialize');
      edit_view.submit();
      assert.isTrue(edit_view.serialize.calledOnce);
      edit_view.serialize.restore();
      done();
    })
  });

  it('should submit the edit and report success', function(done) {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
            'model': node.content
          });
      sinon.spy(edit_view, 'handleSuccess');

      // www.sitepoint.com/unit-testing-backbone-js-applications

      var stub = sinon.stub($, 'ajax').yieldsTo('success', [
          {id: 1, title: 'test', complete: true}
      ]);
      edit_view.submit();
      assert.isTrue(stub.calledOnce);
      assert.isTrue(edit_view.handleSuccess.calledOnce);

      edit_view.handleSuccess.restore();
      stub.restore();
      done();
    })
  });

  it('should submit the edit and report error', function(done) {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
        'model': node.content
      });
      sinon.spy(edit_view, 'handleError');
      var stub = sinon.stub($, 'ajax').yieldsTo('error', [
          {id: 1, title: 'test', complete: false}
      ]);
      edit_view.submit();

      assert.isTrue(stub.calledOnce);
      assert.isTrue(edit_view.handleError.calledOnce);

      edit_view.handleError.restore();
      $.ajax.restore();
      done();
    })
  });

  it('should handleSuccess', function(done) {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
        'model': node.content
      });
      sinon.spy(edit_view, 'close');
      edit_view.handleSuccess();
      assert.isTrue(edit_view.close.calledOnce);
      edit_view.close.restore();
      done();
    })
  });

  it('should handleError', function(done) {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
        'model': node.content
      });
      edit_view.spinner = new Backbone.Spinner();
      edit_view.$el.append('<span id="par"><a name="ev-text1"></a></span>');
      var model = null;
      var xhr = {
        status: 200, // needs additional work to make this work: this['handleError...
        responseText: '{"text1":  "1", "__all__":  "2"}'
      };
      var options = null;
      edit_view.handleError(model, xhr, options);
      assert.deepEqual(edit_view.$el.find('li').eq(0).html(), '2');
      assert.deepEqual(edit_view.$el.find('li').eq(1).html(), '1');
      done();
    })
  });
});

describe('WidgetView', function() {
  beforeEach(function() {
    this.node = new nodes.Node({
      title: 'test',
      content: {
        component: 'testcomponent',
        url: '1',
        edit_url: 'testurl'
      }
    });
  });

  it('should return the editorClass', function(done) {
    return this.node.ready(function(node) {
      assert.strictEqual(node.component.View.prototype.getEditorClass(),
                        node.component.View.prototype.editorClass);
      done();
    })
  });
});
