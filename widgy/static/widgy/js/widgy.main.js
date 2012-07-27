;(function() {
  

  var App = Widgy.View.extend({
    initialize: function() {
      var page = this.options.page,
          content = page.root_node.content;

      var root_node = this.root_node = new Widgy.nodes.NodeView({
        collection: new Widgy.contents.ContentCollection
      });

      this.$el.append(root_node.render().el);

      root_node.collection.add(page.root_node);
    }
  });

  Widgy.main = function(page) {
    Widgy.app = new App({
      page: page,
      el: $('#app')
    });
  };

})();
