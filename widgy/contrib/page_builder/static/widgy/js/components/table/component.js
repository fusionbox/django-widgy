define([ 'widgy.contents', 'widgets/widgets' ], function(contents, widgets) {

  var TableView = widgets.WidgetView.extend({
  });

  var Table = contents.Content.extend({
    viewClass: TableView
  });

  return Table;
});
