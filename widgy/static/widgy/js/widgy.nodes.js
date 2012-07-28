;(function(Widgy) {

  var exports = Widgy.nodes || (Widgy.nodes = {});

  /**
   * Nodes provide structure in the tree.  Nodes only hold data that deals with
   * structure.  Any other data lives in it's content.
   *
   * A node will have two properties: `children` and `content`.  `children` is
   * a NodeCollection which is basically just a list of child nodes. `content`
   * is model containing all non-structure information about a node.  The
   * actual Model Class that defines the content property depends on the
   * content type.  See `widgy.contents.js` for more information.
   */
  var Node = Backbone.Model.extend({
    urlRoot: '/admin/widgy/node/',

    initialize: function() {
      // content gets set because it is in the JSON for the node.  We need to
      // unset it as it is not an attribute, but a property.  We also need to
      // instantiate it as a real Content Model.
      var content = this.get('content');
      this.content = Widgy.contents.instantiateModel(content.object_name, content);
      this.unset('content');

      // same as content.  We need to actually instantiate the NodeCollection
      // and set it as a property, not an attribute.
      var children = this.get('children');
      this.children = new NodeCollection(children);
      this.unset('children');
    }
  });


  /**
   * NodeCollections provide the children interface for nodes and also an
   * interface to NodeViews for how to handle child NodeViews.
   */
  var NodeCollection = Backbone.Collection.extend({
    model: Node,
  });


  /**
   * The NodeView provides an interface to the node.  It will also create a
   * ContentView for the node's content.  Additionally, it will create child
   * NodeViews for all of the nodes in children.
   *
   * Properties:
   *
   * -  `this.model` is the node.  The root node does not have a Node model.
   * -  `this.collection` is the node's children (Also available in
   *    `this.model.children`.
   */
  var NodeView = Widgy.View.extend({
    className: 'node',

    initialize: function() {
      _.bindAll(this, 'addAll', 'addOne');
      this.collection.on('reset', this.addAll);
      this.collection.on('add', this.addOne);

      // The root does not have a model.
      if ( this.model )
        this.model.bind('remove', this.close);
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(node) {
      var node_view = new NodeView({
        model: node,
        collection: node.children
      });

      this.$el.append(node_view.render().el);
    },

    render: function() {
      Widgy.View.prototype.render(this, arguments);

      // The root does not have a model
      if ( this.model )
      {
        var content = this.model.content
            view_class = content.getViewClass();

        this.content_view = new view_class({
          model: content
        });

        this.$el.append(this.content_view.render().el);
      }

      // TODO: investigate possible problems with this.
      this.addAll();

      return this;
    }
  });


  _.extend(exports, {
    Node: Node,
    NodeCollection: NodeCollection,
    NodeView: NodeView
  });

})(this.Widgy);
