define([ 'jquery', 'underscore', 'widgy.backbone', 'lib/csrf', 'lib/q', 'nodes/nodes',
    'text!app.html', 'shelves/shelves'
    ], function($, _, Backbone, csrf, Q, nodes,
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
      this.visible_drop_targets = new Backbone.ViewList();

      var root_node = this.root_node = new nodes.Node(options.root_node),
          app = this;

      this.root_node_promise = root_node.ready(function(model) {
        var root_node_view = new model.component.View({
          model: model,
          app: app,
          tagName: 'section'
        });

        app.node_view_list.push(root_node_view);

        root_node_view
          .on('created', app.node_view_list.push);

        return root_node_view;
      });
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);

      this.$editor = this.$el.children('.editor');
      this.$editor.append(this.root_node_view.render().el);

      return this;
    },

    renderPromise: function() {
      var compatibility_promise = this.fetchCompatibility();

      var render_promise = Q.all([Backbone.View.prototype.renderPromise.apply(this, arguments), this.root_node_promise])
        .spread(function(app, view) {
          app.$editor = app.$el.children('.editor');
          return view.renderPromise().then(function(view) {
            app.$editor.append(view.el);
            view.makeSticky();
          }).thenResolve(app);
        });

      return Q.all([render_promise, compatibility_promise])
        .spread(function(app, compatibility) {
          app.setCompatibility(compatibility);
          return app;
        });
    },

    /**
     * Returns a promise for the root node's compatibility data.
     */
    fetchCompatibility: function() {
      if ( this.inflight )
        this.inflight.abort();

      this.inflight = $.ajax({
        url: this.root_node.get('available_children_url')
      });

      return Q(this.inflight);
    },

    refreshCompatibility: function() {
      this.fetchCompatibility().then(this.setCompatibility).done();
    },

    setCompatibility: function(data) {
      delete this.inflight;

      this.compatibility_data = data;
      this.updateCompatibility(data);
    },

    updateCompatibility: function(data) {
      this.node_view_list.each(function(view) {
        var shelf = view.getShelf();

        if ( shelf )
          shelf.addOptions(data[view.model.id]);
      });
      this.node_view_list.each(function(view) {
        if ( view.hasShelf() && view.shelf )
          view.shelf.filterDuplicates(view);
      });
    },

    validateRelationship: function(parent, child) {
      return _.where(this.compatibility_data[parent.model.id], {'__class__': child.get('__class__')}).length !== 0;
    },

    ready: function() {
      return !!this.compatibility_data;
    }
  });

  $(document).ajaxStart(function() {
    $(this.body).addClass('ajax-loading');
  }).ajaxComplete(function() {
    $(this.body).removeClass('ajax-loading');
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
  function Widgy(target, root_node, url_root) {
    this.app = new AppView({
      root_node: root_node,
      el: $(target)
    });

    nodes.Node.prototype.urlRoot = url_root;

    this.app.renderPromise().done();
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
