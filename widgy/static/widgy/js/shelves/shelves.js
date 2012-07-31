define([ 'underscore', 'widgy.backbone', 'nodes/nodes',
    'text!shelves/shelf_view.html',
    'text!shelves/node_preview_view.html'
    ], function(_, Backbone, nodes,
      shelf_view_template,
      node_preview_view_template
      ) {

  var ShelfCollection = Backbone.Collection.extend({
    url: '/admin/widgy/widgets/',
    model: nodes.Node,

    parse: function(resp) {
      return _.map(resp, function(content_type) {
        return {
          title: content_type['title'],
          __class__: content_type['__class__']
        };
      });
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
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(model) {
      var view = new NodePreviewView({
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


  var NodePreviewView = nodes.NodeViewBase.extend({
    tagName: 'li',
    template: node_preview_view_template,

    'delete': function() {},
  });


  return {
    NodePreviewView: NodePreviewView,
    ShelfCollection: ShelfCollection,
    ShelfView: ShelfView
  };
});
