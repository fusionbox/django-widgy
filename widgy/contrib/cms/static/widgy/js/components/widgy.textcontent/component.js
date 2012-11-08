define([ 'widgy.contents', 'widgets/widgets',
    ], function(
    contents,
    widgets) {

  var EditorView = widgets.EditorView.extend({
  });

  var ContentView = widgets.WidgetView.extend({
    editorClass: EditorView
  });

  var TextContent = contents.Content.extend({
    viewClass: ContentView
  });

  return TextContent;
});
