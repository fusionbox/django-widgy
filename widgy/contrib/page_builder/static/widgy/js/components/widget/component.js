define([ 'widgy.contents', 'widgets/widgets' ], function(contents, widgets) {

  var Content = contents.Content.extend({
    viewClass: widgets.WidgetView
  });

  return Content;
});
