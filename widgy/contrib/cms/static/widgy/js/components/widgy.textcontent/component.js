define([ 'widgy.contents', 'widgets/widgets',
    'text!./content.html',
    'text!./edit.html'
    ], function(contents, widgets,
      content_template,
      edit_content_template
      ) {

  var EditorView = widgets.EditorView.extend({
    template: edit_content_template
  });

  var ContentView = widgets.WidgetView.extend({
    template: content_template,
    editorClass: EditorView
  });

  var TextContent = contents.Content.extend({
    viewClass: ContentView
  });

  return TextContent;
});
