define([ 'widgy.backbone', 'nodes/nodes' ], function(Backbone, nodes) {

  /**
   * Base Model for Contents.  A Content holds the non-structure data for a
   * Node.  While all nodes use the same class, Contents differ based on the
   * Node content type.  As such, we need a special method for accessing
   * Content Model.
   *
   * When you write a Content Model, you need to register that model using
   * `Widgy.contents.registerModel`.  This way other parts of Widgy have access
   * to the custom Content Model.  You must provide a viewClass property on
   * your Content Model in for NodeView to know which ContentView to render.
   */
  var Content = Backbone.Model.extend({
    initialize: function(attributes, options) {
      Backbone.Model.prototype.initialize.apply(this, arguments);

      // debugging: this will go away later probably.
      this.type = this.get('model');
      this.node = options.node;
    }
  });


  /**
   * Base View for Contents.  A Content View displays the Content and also
   * provides an interface to edit it.  Usually, the ContentView just shows
   * Content and when the user wishes to edit the content, it will open another
   * view.  See `widgy.widgets.js`.
   */
  var ContentView = Backbone.View.extend({
    className: 'content',

    initialize: function(options) {
      this.listenTo(this.model, 'change:preview_template', this.render);
    },

    getTemplate: function() {
      return this.model.get('preview_template');
    }
  });


  return {
    Content: Content,
    View: nodes.NodeView
  };
});
