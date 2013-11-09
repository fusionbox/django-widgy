define([ 'jquery', 'underscore', 'widgy.backbone', 'nodes/base',
    'nodes/models',
    'text!nodes/preview.html',
    'text!./shelf.html'
    ], function($, _, Backbone, DraggableView,
      node_models,
      shelf_item_view_template,
      shelf_view_template
      ) {

  var ShelfCollection = Backbone.Collection.extend({
    comparator: 'title',
    model: node_models.Node,

    initialize: function(options) {
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
        'filterDuplicates',
        'resizeShelf'
      );

      this.collection.on('add', this.addOne);

      this.app = options.app;

      this.list = new Backbone.ViewList();
    },

    addOne: function(model) {
      var view = new ShelfItemView({
        model: model,
        app: this.app
      });

      view.on('all', this.bubble);

      this.list.push(view);
    },

    resort: function(collection) {
      _.each(collection.models, function(model) {
        var view = this.list.findByModel(model);
        this.$list.append(view.el);
      }, this);

      if ( collection.length == 0 )
        this.$el.addClass('empty');
      else
        this.$el.removeClass('empty');

    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);
      this.$scroll = this.$el.find('> .scroll');
      var $list = this.$list = this.$scroll.find('> .list');
      this.collection.on('sort', this.resort);

      this.list.on('push', function(view) {
        $list.append(view.render().el);
      });

      this.resizeShelf();
      $(window).resize(this.resizeShelf);
      return this;
    },

    resizeShelf: function() {
      var mezzanine_correction = 125;
      this.$scroll.css({'max-height': document.documentElement.clientHeight - mezzanine_correction});
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
          return this.collection._prepareModel(value);
      }, this);
      this.collection.set(instances);
      this.collection.sort();
      this.content_classes = null;
    },

    onClose: function() {
      Backbone.View.prototype.onClose.apply(this, arguments);
      $(window).off('resize', this.resizeShelf);
    }
  });


  var ShelfItemView = DraggableView.extend({
    tagName: 'li',
    className: 'shelfItem',
    template: shelf_item_view_template,

    // Override the DraggableView events, I want the whole thing draggable, not
    // just the drag handle.
    events: Backbone.extendEvents(DraggableView, {
      'mousedown': 'onMouseDown'
    }),

    canAcceptParent: function(parent) {
      return this.app.validateRelationship(parent, this.model);
    },

    onMouseDown: function(event) {
      var ret = DraggableView.prototype.onMouseDown.apply(this, arguments);

      if (ret)
        this.startBeingDragged(event);
    },

    startBeingDragged: function(event) {
      this.placeholder = this.$el.clone()
        .css({'visibility': 'hidden'})
        .insertAfter(this.$el);

      DraggableView.prototype.startBeingDragged.apply(this, arguments);
    },

    stopBeingDragged: function() {
      DraggableView.prototype.stopBeingDragged.apply(this, arguments);
      this.placeholder.remove();
    },

    cssClasses: function() {
      return this.model.get('css_classes');
    },

    render: function() {
      DraggableView.prototype.render.apply(this, arguments);
      this.$el.attr('title', this.model.get('tooltip'));
      return this;
    }

  });


  return {
    ShelfCollection: ShelfCollection,
    ShelfView: ShelfView
  };
});
