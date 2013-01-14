define([ 'exports', 'underscore', 'widgy.backbone', 'nodes/nodes',
    'text!./shelf.html'
    ], function(exports, _, Backbone, nodes,
      shelf_view_template
      ) {

  var ShelfCollection = Backbone.Collection.extend({
    initialize: function(options) {
      _.bindAll(this,
        'refresh'
      );

      this.model = nodes.Node;

      this.node = options.node;
      this.on('remove', this.refresh);
    },

    url: function() {
      return this.node.get('available_children_url');
    },

    refresh: function() {
      // IE tries to cache this
      this.fetch({cache: false});
    }
  });

  var ShelfView = Backbone.View.extend({
    className: 'shelf',
    template: shelf_view_template,

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'addOne',
        'addAll',
        'refresh'
      );

      this.collection
        .on('reset', this.addAll)
        .on('add', this.addOne);

      this.app = options.app;

      this.list = new Backbone.ViewList();
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

      view.on('all', this.bubble);

      this.list.push(view);
      this.$list.append(view.render().el);
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);
      this.$list = this.$el.children('.list');

      return this;
    },

    refresh: function() {
      this.collection.refresh();
    },

    validParentOf: function(parent_id, child_class) {
      var data = this.collection.where({'__class__': child_class});
      console.log(data);
      return data.length && _.contains(data[0].get('possible_parent_nodes'), parent_id);
    }
  });


  _.extend(exports, {
    ShelfCollection: ShelfCollection,
    ShelfView: ShelfView
  });
});
