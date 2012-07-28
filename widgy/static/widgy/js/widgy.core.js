;(function() {

  var exports = this.Widgy || (this.Widgy = {});

  /**
   * Our base Backbone classes.
   */
  var View = Backbone.View.extend({
    /**
     * Adds a method for killing zombies.
     *
     * Based on Derick Bailey's blog post:
     * http://lostechies.com/derickbailey/2011/09/15/zombies-run-managing-page-transitions-in-backbone-apps/
     */
    close: function() {
      this.remove();
      this.undelegateEvents();
      this.onClose();
      this.trigger('close', this);
    },

    onClose: function() {},

    template: false,

    render: function() {
      if (this.template) {
        this.$el.html(ich[this.template](this.model.toJSON()));
      }

      return this;
    }
  });


  var AppView = View.extend({
    initialize: function(options) {
      var page = options.page;

      var collection = new Widgy.nodes.NodeCollection(page.root_node);
      var root_view = this.root_view = new Widgy.nodes.NodeView({
        collection: collection,
      });

      this.$el.html(root_view.render().el);
    }
  });


  function main(page) {
    exports.app = new AppView({
      page: page,
      el: $('#app')
    });
  }

  
  _.extend(exports, {
    View: View,
    Widgy: AppView,
    main: main
  });
})();
