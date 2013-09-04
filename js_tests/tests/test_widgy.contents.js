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
  it('should check if editable - false', function() {
    var node = new nodes.Node({
      content: {
        component: 'testcomponent',
      }
    });
    return node.ready(function() {
      assert.isFalse(node.content.isEditable());
    })
    .done();
  });

  it('should check if editable - true', function() {
    var node = new nodes.Node({
      content: {
        component: 'testcomponent',
        edit_url: 'testurl'
      }
    });
    return node.ready(function() {
      assert.isTrue(node.content.isEditable());
    })
    .done();
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

  it('should return template', function() {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
            'model': node.content
          });
      var simulated_ajax_response = {
        template: '<span><%title%></span>',
        edit_template: '<span><%edit_template%></span>'
      };
      var myAPI = function() {return Q(simulated_ajax_response);};
      var stub = sinon.stub($, 'ajax', myAPI);
      var template_promise = edit_view.getTemplate();

      template_promise.then(function(temp) {
        assert.deepEqual(temp, '<span><%edit_template%></span>');
      })
      .done();
      $.ajax.restore();
    })
    .done();
  });

  it('should submit and call serialize', function() {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
            'model': node.content
          });
      sinon.spy(edit_view, 'serialize');
      edit_view.submit();
      assert.isTrue(edit_view.serialize.calledOnce);
      edit_view.serialize.restore();
    })
    .done();
  });

  it('should submit the edit and report success', function() {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
            'model': node.content
          });
      sinon.spy(edit_view, 'handleSuccess');
      var myAPI = function() { return {
        model: node.content,
        respones: 'test',
        options: {success: true}
      }};

      // www.sitepoint.com/unit-testing-backbone-js-applications

      var stub = sinon.stub($, 'ajax').yieldsTo('success', [
          {id: 1, title: 'test', complete: true}
      ]);
      edit_view.submit();
      assert.isTrue(stub.calledOnce);
      assert.isTrue(edit_view.handleSuccess.calledOnce);

      edit_view.handleSuccess.restore();
      $.ajax.restore();
    })
    .done();
  });

  it('should submit the edit and report error', function() {
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
    })
    .done();
  });

  it('should handleSuccess', function() {
    return this.node.ready(function(node) {
      var edit_view = new contents.EditorView({
        'model': node.content
      });
      sinon.spy(edit_view, 'close');
      edit_view.handleSuccess();
      assert.isTrue(edit_view.close.calledOnce);
      edit_view.close.restore();
    })
    .done();
  });

  it('should handleError', function() {
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
    })
    .done();
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

  it('should return the editorClass', function() {
    return this.node.ready(function(node) {
      assert.strictEqual(node.component.View.prototype.getEditorClass(),
                        node.component.View.prototype.editorClass);
    })
    .done();
  });

  /**
    * TODO editWidget Tests do not completely test this method; also, the stub
    *      prevents complete testing of the promise chain. The issue is from
    *      editorClass adding a 'prototype'layer to the methods for example:
    *        EditorView.getTemplate roughly turns into
    *        EditorView.prototype.getTemplate
    */
  it('should editWidget successfully', function() {
    return this.node.ready(function(node) {
      var eve = new $.Event();
      var widget_view = new contents.View({model: node});
      widget_view.$el.append('<button class="edit"></button>');
      widget_view.$el.append(
        '<span class="widget"><span class="preview">Initial Preview</span></span>');
      widget_view.editorClass.prototype.el = '<div>Changed Preview</div>';
      widget_view.$preview = widget_view.$(' > .widget > .preview ');
      widget_view.$children = widget_view.$(' > .widget > .node_chidren ');
      widget_view.editorClass.prototype.template = '<div><%title%></div>';

      var myAPI = function() {return {edit_template: '<div class="temp"><%title%></div>'};};
      sinon.stub(widget_view.editorClass.prototype, 'getTemplate', myAPI);

      widget_view.editWidget(eve);
      widget_view.editorClass.prototype.el = undefined;
      widget_view.editorClass.prototype.getTemplate.restore();

      assert.deepEqual(widget_view.$preview.html(), '<div>Changed Preview</div>');
    })
    .done();
  });

  it('should editWidget and fail', function() {
    // throws error from EditorView.getTemplate() not working in this instance.
    // TODO create a way to capture the error without breaking the tests.

    return this.node.ready(function(node) {
      var eve = new $.Event();
      var widget_view = new contents.View({model: node});
      widget_view.$el.append('<span class="edit"></span>');
      widget_view.$preview = widget_view.$(' > .widget > .preview ');
      widget_view.$children = widget_view.$(' > .widget > .node_chidren ');
      //widget_view.editWidget(eve);
    })
    .done();
  });
});
