define([ 'widgy.contents', 'widgets/widgets'
], function(contents, widgets) {

  var EditorView = widgets.EditorView.extend({});

  var LayoutView = contents.ContentView.extend({
    editorClass: EditorView
    });

  var TwoColumnLayout = contents.Content.extend({
    viewClass: LayoutView
  });

  return TwoColumnLayout;
});
