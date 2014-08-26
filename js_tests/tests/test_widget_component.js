var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var _ = requirejs('underscore'),
    Q = requirejs('lib/q'),
    $ = requirejs('jquery'),
    form = requirejs('form'),
    contents = requirejs('widgy.contents'),
    nodes = requirejs('nodes/nodes'),
    sinon = requirejs('sinon');

var TestComponent = requirejs('components/testcomponent/component');


describe('FormView', function() {
  describe('it knows how to serialize', function() {
    it('various input types', function() {
      var form_view = new form.FormView();

      form_view.$el.html('<input type="text" name="text" value="1">' +
                         '<input type="radio" name="radio" value="2-a">' +
                         '<input type="radio" name="radio" value="2-b" checked>' +
                         '<input type="radio" name="radio" value="2-c">' +
                         '<input type="checkbox" name="checkbox" value="2-a">' +
                         '<input type="checkbox" name="checkbox" value="2-b" checked>' +
                         '<input type="checkbox" name="checkbox" value="2-c">' +
                         '<select name="select"><option value="1">1</option><option value="2" selected></option></select>' +
                         '<textarea name="textarea">text</textarea>'
                         );

      assert.deepEqual(form_view.serialize(), {
        'text': '1',
        'radio': '2-b',
        'checkbox': '2-b',
        'select': '2',
        'textarea': 'text'
      });
    });

    it.skip('handles multiple checkbox selections', function() {
      var form_view = new form.FormView();

      form_view.$el.html('<input type="checkbox" name="checkbox" value="2-a">' +
                         '<input type="checkbox" name="checkbox" value="2-b" checked>' +
                         '<input type="checkbox" name="checkbox" value="2-c" checked>'
                         );

      var values = form_view.serialize();

      assert.include(values.checkbox, '2-b');
      assert.include(values.checkbox, '2-c');
      assert.lengthOf(values.checkbox, 2);
    });

    it('handles select multiple', function() {
      var form_view = new form.FormView();

      form_view.$el.html('<select name="select" multiple><option value="1"><option value="2" selected><option value="3" selected></select>');

      var values = form_view.serialize();

      assert.include(values.select, '2');
      assert.include(values.select, '3');
      assert.lengthOf(values.select, 2);
    });
  });

  it('should only submit if left clicked', function() {
    var form_view = new form.FormView(),
        evt = $.Event();
    evt.target = { disabled: false };
    evt.which = 3;
    assert.isTrue(form_view.handleClick(evt));
  });

  it('should not submit if the submit button is disabled', function() {
    var form_view = new form.FormView(),
        evt = $.Event();
    evt.target = { disabled: true };
    evt.which = 3;
    assert.isFalse(form_view.handleClick(evt));
  });

  it('should handleKeypress', function() {
    var form_view = new form.FormView(),
        evt = $.Event();
    evt.which = 13;
    assert.isFalse(form_view.handleKeypress(evt)); // prevent default
  });

  it('should close CKEDITOR', function() {
    test.create();
    var callback = sinon.spy();
    var form_view = new form.FormView();
    form_view.$el.append('<div class="widgy_ckeditor" id="0"></div>');
    window.CKEDITOR = new Object({instances: []});
    window.CKEDITOR.instances[0] = new Object({
      id: '0',
      destroy: callback
    });
    form_view.close();
    assert.isTrue(callback.calledOnce);
    test.destroy();
  });
});

describe('Editor', function() {
  beforeEach(function() {
    this.node = new nodes.Node({
      content: {
        component: 'testcomponent',
        form_prefix: '23'
      }
    });
  });

  var create_editor = function(node) {
    return new node.component.View.prototype.editorClass({
      'model': node.content
    });
  };

  describe('knows how to deal with prefixes', function() {
    it('field name method', function() {
      return this.node.ready(function(node) {
        var edit_view = create_editor(node);

        assert.equal(edit_view.getPrefixedFieldName('xxx'), '23-xxx');
        assert.equal(edit_view.removeFieldNamePrefix('23-xxx'), 'xxx');
        assert.equal(edit_view.removeFieldNamePrefix('24-xxx'), '24-xxx');
      });
    });

    it('in form hydration', function() {
      return this.node.ready(function(node) {
        var edit_view = create_editor(node);

        edit_view.$el.html('<input name="23-foo" value="1">' +
                           '<input name="24-bar" value="2">' +
                           '<input name="23-foo-foo" value="3">'
                           );

        assert.deepEqual(edit_view.serialize(), {
          'foo': '1',
          '24-bar': '2',
          'foo-foo': '3'
        });
      });
    });
  });
});
