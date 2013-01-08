define([ 'jquery', 'underscore', 'widgy.backbone', 'nodes/nodes',
    'text!app.html'
    ], function($, _, Backbone, nodes,
      app_template
      ) {

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
    template: app_template,

    initialize: function(options) {
      // instantiate node_view_list before creating the root node
      // please!
      this.node_view_list = new Backbone.ViewList();

      var root_node_view = this.root_node_view = new nodes.NodeView({
        model: new nodes.Node(options.root_node),
        app: this,
        tagName: 'section',
        rootNode: true
      });

      this.node_view_list.push(root_node_view);

      root_node_view
        .on('created', this.node_view_list.push);
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);

      this.$editor = this.$el.children('.editor');
      this.$editor.append(this.root_node_view.render().el);

      return this;
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
  function Widgy(target, root_node) {
    this.app = new AppView({
      root_node: root_node,
      el: $(target)
    });

    this.app.render();
  }

  function actAsPopOut() {
    if ( window.widgyCloseCallback ) {
      $(window).on('unload', window.widgyCloseCallback);
    }
  }

  return _.extend(Widgy, {
    AppView: AppView,
    actAsPopOut: actAsPopOut
  });
});
