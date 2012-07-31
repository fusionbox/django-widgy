define([ 'underscore', 'widgy.backbone', 'nodes/nodes',
    'text!shelves/shelf_view.html'
    ], function(_, Backbone, nodes,
      shelf_view_template
      ) {

  var ShelfCollection = Backbone.Collection.extend({
    url: '/admin/widgy/widgets/',
    model: nodes.Node
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
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(model) {
      var view = new nodes.NodePreviewView({
        model: model,
        app: this.app
      });

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
