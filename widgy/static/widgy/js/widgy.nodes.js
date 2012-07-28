;(function(Widgy) {

  var exports = Widgy.nodes || (Widgy.nodes = {});

  var Node = Backbone.Model.extend({
    urlRoot: '/admin/widgy/node/',

    initialize: function() {
      var content = this.get('content');
      this.content = Widgy.contents.instantiateModel(content.object_name, content);
      this.unset('content');

      var children = this.get('children');
      this.children = new NodeCollection(children);
      this.unset('children');
    }
  });


  var NodeCollection = Backbone.Collection.extend({
    model: Node,
  });


  var NodeView = Widgy.View.extend({
    className: 'node',

    initialize: function() {
      _.bindAll(this, 'addAll', 'addOne');
      this.collection.on('reset', this.addAll);
      this.collection.on('add', this.addOne);

      // The root does not have a model.
      if ( this.model )
        this.model.bind('remove', this.close, this);
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

      if ( this.model )
      {
        var content = this.model.content;
        this.content_view = new content.viewClass({
          model: content
        });
        this.$el.append(this.content_view.render().el);
      }

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
