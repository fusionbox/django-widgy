define([ 'jquery', 'widgy.backbone', 'nodes/nodes' ], function($, Backbone, nodes) {

  /**
   * This is the view that handles the entire widgy App.  It will take the page
   * data and create the root node.
   *
   * The AppView also acts as a mediator object for things like drag and drop.
   * For example, when a node is being dragged, it informs the AppView, which
   * can in turn tell the rest of the app to make itself droppable.  Every node
   * has a reference to the instance of the AppView.
   */
  var AppView = Backbone.View.extend({
    initialize: function(options) {
      _.bindAll(this,
        'startDrag',
        'stopDrag'
      );

      var page = options.page;

      // instantiate node_view_list before creating the root node
      // please!
      this.node_view_list = new Backbone.ViewList;

      var root_node = new nodes.Node(page.root_node);
      var root_node_view = this.root_node_view = new nodes.NodeView({
        model: root_node,
        collection: root_node.children,
        app: this
      });

      this.$el.html(root_node_view.el);
    },

    startDrag: function(dragged_view) {
      this.dragged_view = dragged_view;

      $(document).on('mouseup.' + dragged_view.cid, this.stopDrag);
      $(document).on('mousemove.' + dragged_view.cid, dragged_view.followMouse);
      // TODO: follow mouse on scroll.

      this.node_view_list.each(function(node_view) {
        node_view.becomeDropTarget();
      });
    },

    stopDrag: function() {
      var dragged_view = this.dragged_view;
      delete this.dragged_view;

      $(document).off('.' + dragged_view.cid);

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

  return _.extend(Widgy, {
    AppView: AppView
  });
});
