var test = require('./setup').test,
    requirejs = require('requirejs'),
    assert = require('chai').assert;

var _ = requirejs('underscore'),
    Q = requirejs('lib/q'),
    form = requirejs('form'),
    contents = requirejs('widgy.contents'),
    nodes = requirejs('nodes/nodes');

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
});

describe('Editor', function() {
  describe('knows how to deal with prefixes', function() {
    beforeEach(function() {
      this.node = new nodes.Node({
        content: {
          component: 'testcomponent',
          form_prefix: '23'
        }
      });
    });

    it('field name method', function() {
      return this.node.ready(function(node) {
        var cls = node.component.View.prototype.editorClass,
            edit_view = new cls({
              'model': node.content
            });

        assert.equal(edit_view.getPrefixedFieldName('xxx'), '23-xxx');
        assert.equal(edit_view.removeFieldNamePrefix('23-xxx'), 'xxx');
        assert.equal(edit_view.removeFieldNamePrefix('24-xxx'), '24-xxx');
      });
    });

    it('in form hydration', function() {
      return this.node.ready(function(node) {
        var cls = node.component.View.prototype.editorClass,
            edit_view = new cls({
              'model': node.content
            });

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
