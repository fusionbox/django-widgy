;(function() {

  var exports = this.Widgy || (this.Widgy = {});

  /**
   * Our base Backbone classes.
   */
  var View = Backbone.View.extend({
    constructor: function() {
      Backbone.View.prototype.constructor.apply(this, arguments);

      _.bindAll(this, 'close', 'render');
    },
    /**
     * Adds a method for killing zombies.
     *
     * Based on Derick Bailey's blog post:
     * http://lostechies.com/derickbailey/2011/09/15/zombies-run-managing-page-transitions-in-backbone-apps/
     */
    close: function(event) {
      if ( event ) {
        event.preventDefault();
      }

      this.remove();
      this.undelegateEvents();
      this.onClose();
      this.trigger('close', this);
    },

    onClose: function() {},

    template: false,

    /**
     * If your subclass has a template property, render will use ICanHaz to
     * render the template and passes in `model.toJSON()`.
     */
    render: function() {
      if (this.template) {
        var context = this.model ? this.model.toJSON() : {};
        this.$el.html(this.renderTemplate(this.template, context));
      }

      return this;
    },

    renderTemplate: function(template_name, context) {
      return ich[template_name](context);
    }
  });


  var Model = Backbone.Model.extend({
    url: function() {
      var base_url = Backbone.Model.prototype.url.apply(this, arguments);

      if ( base_url.charAt(base_url.length - 1) !== '/' )
        base_url += '/';
      
      return base_url;
    }
  });


  var AppView = View.extend({
    initialize: function(options) {
      var page = options.page;

      var root_node = new Widgy.nodes.Node(page.root_node);
      var root_view = this.root_view = new Widgy.nodes.NodeView({
        model: root_node,
        collection: root_node.children
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
    Model: Model,
    Widgy: AppView,
    main: main
  });
})();
