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


  return {
    Model: Content,
    View: nodes.NodeView
  };
});
