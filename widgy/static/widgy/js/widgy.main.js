;(function() {
  

  var App = Backbone.View.extend({
    initialize: function() {
      var page = this.options.page,
          content = page.root_node.content;

      var root_content = Widgy.contents.createContent(content);
      var root_node = this.root_node = Widgy.nodes.createNode(root_content);

      this.$el.append(root_node.widgyRender().el);
    }
  });

  Widgy.main = function(page) {
    app = new App({page: page, el: $('#app')});
  };

})();
