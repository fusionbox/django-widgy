define([ 'widgy.contents', 'widgets/widgets'
    ], function(
    contents,
    widgets) {

  var ContentView = widgets.WidgetView.extend({
    editorClass: widgets.EditorView
  });

  var ExampleContent = contents.Content.extend({
    viewClass: ContentView
  });

  return ExampleContent;
});
