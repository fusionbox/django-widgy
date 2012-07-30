define([ 'widgy.contents' ], function(contents) {

  var LayoutView = contents.ContentView.extend({});

  var TwoColumnLayout = contents.Content.extend({
    viewClass: LayoutView
  });

  return TwoColumnLayout;
});
