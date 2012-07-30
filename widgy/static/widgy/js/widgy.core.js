;(function() {

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
    idAttribute: 'url',

    url: function() {
      return this.id;
    }
  });


  var AppView = View.extend({
    initialize: function(options) {
      var page = options.page;

      // instantiate node_view_list before creating the root node
      // please!
      this.node_view_list = new Widgy.nodes.NodeViewList;

      var root_node = new Widgy.nodes.Node(page.root_node);
      var root_node_view = this.root_node_view = new Widgy.nodes.NodeView({
        model: root_node,
        collection: root_node.children,
        app: this
      });

      this.$el.html(root_node_view.render().el);
    },

    startDrag: function(dragged_view) {
      this.dragged_view = dragged_view;

      this.node_view_list.each(function(node_view) {
        node_view.becomeDropTarget();
      });
    },

    stopDrag: function() {
      var dragged_view = this.dragged_view;
      delete this.dragged_view;

      this.node_view_list.each(function(node_view) {
        node_view.clearPlaceholders();
      });

      dragged_view.stopDrag();
      return dragged_view;
    }
  });


  function Widgy(jqueryable, page) {
    this.app = new AppView({
      page: page,
      el: $(jqueryable)
    });
  }


  var exports = this.Widgy = Widgy;
  

  _.extend(exports, {
    View: View,
    Model: Model,
    Widgy: AppView
  });
})();
