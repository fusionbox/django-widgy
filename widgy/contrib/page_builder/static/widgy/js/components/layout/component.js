define([ 'widgy.contents' ], function(contents) {

  var LayoutView = contents.ContentView.extend();

  var Layout = contents.Content.extend({
    viewClass: LayoutView
  });

  return Layout;
});
