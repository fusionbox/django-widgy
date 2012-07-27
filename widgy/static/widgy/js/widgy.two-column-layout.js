;(function() {


  var TwoColumnLayout = Widgy.contents.TwoColumnLayout = Widgy.contents.ContentModel.extend({
    viewClass: 'LayoutView'
  });

  
  var LayoutView = Widgy.nodes.LayoutView = Widgy.nodes.NodeView.extend({
    render: Widgy.noop
  });
})();
