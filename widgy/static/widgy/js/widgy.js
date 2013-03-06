define([ 'jquery', 'underscore', 'widgy.backbone', 'lib/csrf', 'nodes/nodes',
    'nodes/models',
    'text!app.html', 'shelves/shelves'
    ], function($, _, Backbone, csrf, nodes,
      node_models,
      app_template, shelves
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
      Backbone.View.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'refreshCompatibility',
        'setCompatibility',
        'validateRelationship',
        'ready'
      );

      // instantiate node_view_list before creating the root node
      // please!
      this.node_view_list = new Backbone.ViewList();

      var root_node_view = this.root_node_view = new nodes.NodeView({
        model: new node_models.Node(options.root_node),
        app: this,
        tagName: 'section'
      });

      this.node_view_list.push(root_node_view);

      root_node_view
        .on('created', this.node_view_list.push);

      this.refreshCompatibility();
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);

      this.$editor = this.$el.children('.editor');
      this.$editor.append(this.root_node_view.render().el);

      return this;
    },

    refreshCompatibility: function() {
      if ( this.inflight )
        this.inflight.abort();

      this.inflight = $.ajax({
        url: this.root_node_view.model.get('available_children_url'),
        success: this.setCompatibility,
      });
    },

    setCompatibility: function(data) {
      console.log('setCompatibility', data);
      delete this.inflight;

      this.compatibility_data = data;
      this.node_view_list.each(function(view) {
        var shelf = view.getShelf()
        if ( shelf )
          shelf.addOptions(data[view.model.id]);
      });
      this.node_view_list.each(function(view) {
        if ( view.hasShelf() )
          view.shelf.filterDuplicates(view);
      });
    },

    validateRelationship: function(parent, child) {
      return _.where(this.compatibility_data[parent.model.id], {'__class__': child.get('__class__')}).length != 0;
    },

    ready: function() {
      return !!this.compatibility_data;
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
      $(window).on('unload.widgyPopOut', window.widgyCloseCallback);
    }
  }

  return _.extend(Widgy, {
    AppView: AppView,
    actAsPopOut: actAsPopOut
  });
});
