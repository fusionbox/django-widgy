define([ 'underscore', 'widgy.backbone', 'nodes/nodes',
    'text!./shelf.html'
    ], function(_, Backbone, nodes,
      shelf_view_template
      ) {

  var ShelfCollection = Backbone.Collection.extend({
    model: nodes.Node,

    initialize: function(options) {
      _.bindAll(this,
        'update'
      );

      this.node = options.node;
      this.on('remove', this.update);
    },

    url: function() {
      return this.node.get('available_children_url');
    },

    update: function() {
      // TODO: instead of a destructive overwriting, we need to merge the
      // things on the shelf.  With the return, we need to delete any widgets
      // that are no longer acceptable children and add the new widgets,
      // without modifying ones that haven't changed.
      this.fetch();
    }
  });

  var ShelfView = Backbone.View.extend({
    className: 'shelf',
    template: shelf_view_template,

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'addOne',
        'addAll'
      );

      this.collection
        .on('reset', this.addAll)
        .on('add', this.addOne);

      this.app = options.app;

      this.list = new Backbone.ViewList;
    },

    addAll: function() {
      this.list.closeAll();
      this.collection.each(this.addOne);
    },

    addOne: function(model) {
      var view = new nodes.NodePreviewView({
        model: model,
        app: this.app
      });

      this.list.push(view);
      this.$list.append(view.render().el);
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);
      this.$list = this.$el.children('.list');

      return this;
    }
  });


  return {
    ShelfCollection: ShelfCollection,
    ShelfView: ShelfView
  };
});
