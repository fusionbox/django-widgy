require.config({
  shim: {
    'pagedown': {
      deps: ['pagedown-converter', 'pagedown-sanitizer'],
      exports: 'Markdown'
    },
    'pagedown-sanitizer': {
      deps: ['pagedown-converter']
    }
  },
  paths: {
    'pagedown': 'components/markdown/lib/Markdown.Editor',
    'pagedown-converter': 'components/markdown/lib/Markdown.Converter',
    'pagedown-sanitizer': 'components/markdown/lib/Markdown.Sanitizer'
  }
});

define([ 'underscore', 'components/widget/component', 'pagedown' ], function(_, widget, Markdown) {

  var idPostfix = 1;

  var MarkdownEditorView = widget.EditorView.extend({
    renderHTML: function() {
      widget.EditorView.prototype.renderHTML.apply(this, arguments);

      var textarea = this.$('textarea[name=' + this.getPrefixedFieldName('content') + ']')[0],
          preview = this.$('.pagedown-preview')[0],
          buttonBar = this.$('.pagedown-buttonbar')[0],
          converter = Markdown.getSanitizingConverter();

      var editor = new Markdown.Editor(converter, textarea, preview, buttonBar, {
        idPostfix: idPostfix++
      });

      editor.run();

      return this;
    }
  });

  var MarkdownView = widget.View.extend({
    editorClass: MarkdownEditorView
  });

  return _.extend({}, widget, {
    View: MarkdownView
  });
});
