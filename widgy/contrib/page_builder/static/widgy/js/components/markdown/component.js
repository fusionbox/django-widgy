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

define([ 'widgy.contents', 'widgets/widgets', 'pagedown' ], function(contents, widgets, Markdown) {

  var idPostfix = 1;

  var MarkdownEditorView = widgets.EditorView.extend({
    renderHTML: function() {
      widgets.EditorView.prototype.renderHTML.apply(this, arguments);

      var textarea = this.$('textarea[name=content]')[0],
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

  var MarkdownView = widgets.WidgetView.extend({
    editorClass: MarkdownEditorView
  });

  var Content = contents.Content.extend({
    viewClass: MarkdownView
  });

  return Content;
});
