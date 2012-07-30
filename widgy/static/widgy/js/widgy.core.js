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

    /**
     * If your subclass has a template property, render will use ICanHaz to
     * render the template and passes in `model.toJSON()`.
     */
    template: false,

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


  /**
   * None of our models use ids, they all use URLs to communicate with the
   * server.  See `widgy/models.py` for more on how to expose the URL.
   */
  var Model = Backbone.Model.extend({
    idAttribute: 'url',

    url: function() {
      return this.id;
    }
  });


  /**
   * Maintains an app "global" list of Views so that you can find them using
   * their properties, such as their `el` or their model's id.
   *
   * The AppView has an instance of this list to keep track of all of the node
   * views.
   */
  function ViewList() {
    this.list = []
  }

  _.extend(ViewList.prototype, {
    push: function(view) {
      this.list.push(view);
    },

    each: function(iterator, context) {
      return _.each(this.list, iterator, context);
    },

    find: function(finder) {
      return _.find(this.list, finder);
    },

    findById: function(id) {
      return this.find(function(view) {
        return id === view.model.id;
      });
    },

    findByEl: function(el) {
      return this.find(function(view) {
        return el === view.el;
      });
    }
  });


  /**
   * This is the view that handles the entire widgy App.  It will take the page
   * data and create the root node.
   *
   * The AppView also acts as a mediator object for things like drag and drop.
   * For example, when a node is being dragged, it informs the AppView, which
   * can in turn tell the rest of the app to make itself droppable.  Every node
   * has a reference to the instance of the AppView.
   */
  var AppView = View.extend({
    initialize: function(options) {
      var page = options.page;

      // instantiate node_view_list before creating the root node
      // please!
      this.node_view_list = new ViewList;

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


  /**
   * Wrapper class to create a new instance of a Widgy editor.  The constructor
   * accepts two parameters.  The first is either a selector, a DOM element, or
   * a jQuery object which will be the element for the app.  The second is the
   * page data object.
   *
   * This is to encourage non-global oriented design.  By exposing a
   * constructor, we are encouraged to think of the Widgy editor as an
   * instance.  This way we don't have global variables in our code.
   */
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
    Widgy: AppView,
    ViewList: ViewList
  });
})();
