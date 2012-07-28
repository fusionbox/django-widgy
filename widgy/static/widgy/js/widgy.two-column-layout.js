;(function(Widgy) {


  var LayoutView = Widgy.contents.ContentView.extend({});

  var TwoColumnLayout = Widgy.contents.Content.extend({
    viewClass: LayoutView
  });

  Widgy.contents.registerModel('TwoColumnLayout', TwoColumnLayout);


})(this.Widgy);
