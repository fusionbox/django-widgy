define([ 'exports', 'underscore', 'widgy.backbone', 'nodes/nodes',
    'text!./shelf.html'
    ], function(exports, _, Backbone, nodes,
      shelf_view_template
      ) {

  var ShelfCollection = Backbone.Collection.extend({
    comparator: 'title',

    initialize: function(options) {
      this.model = nodes.Node;

      this.node = options.node;
    }
  });

  var ShelfView = Backbone.View.extend({
    className: 'shelf',
    template: shelf_view_template,

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'addOne',
        'resort',
        'refresh',
        'addOptions',
        'filterDuplicates'
      );

      this.collection.on('add', this.addOne)
                     .on('sort', this.resort);

      this.app = options.app;

      this.list = new Backbone.ViewList();
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

    resort: function(collection) {
      _.each(collection.models, function(model) {
        var view = this.list.findByModel(model);
        this.$list.append(view.el);
      }, this);
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);
      this.$list = this.$el.children('.list');

      return this;
    },

    refresh: function() {
      this.app.refreshCompatibility();
    },

    addOptions: function(content_classes) {
      this.content_classes = this.content_classes || {};
      _.each(content_classes, function(content_class) {
        this.content_classes[content_class.__class__] = content_class;
      }, this);
    },

    /**
     * Using the list that addOptions built up, determine whether or not a
     * NodePreview should live on this shelf. Then, update the collection
     * non-destructively.
     */
    filterDuplicates: function(parent_view) {
      var seen_classes = [];
      parent_view = parent_view.parent

      // filter out items that are on one of our parent shelves
      while ( parent_view )
      {
        if (parent_view.hasShelf())
        {
          _.each(parent_view.getShelf().collection.toJSON(), function(data) {
            delete this.content_classes[data.__class__];
          }, this);
        }
        parent_view = parent_view.parent;
      }

      // we need the same instance of the Node, so that update won't destroy our
      // view, which might be being dragged. This allows people to add things
      // while the shelf is being refreshed.
      var instances = _.map(this.content_classes, function(value, key) {
        var existing = this.collection.where({__class__: key});
        if ( existing.length )
          return existing[0];
        else
          return new nodes.Node(value);
      }, this);
      this.collection.update(instances);
      this.collection.sort();
      this.content_classes = null;
    }
  });


  _.extend(exports, {
    ShelfCollection: ShelfCollection,
    ShelfView: ShelfView
  });
});
