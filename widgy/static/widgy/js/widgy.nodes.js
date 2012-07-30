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
  var Node = Widgy.Model.extend({
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
   * Maintains an app "global" list of all NodeViews so that you can find them
   * using their properties, such as their `el` or their model's id.
   *
   * The AppView has an instance of this list.
   *
   * TODO: This list is not specific to NodeViews, might as well not put it
   * under Widgy.nodes.  Move this to Widgy.ViewList.
   */
  function NodeViewList() {
    this.list = []
  }

  _.extend(NodeViewList.prototype, {
    push: function(view) {
      this.list.push(view);
    },

    each: function(iterator, context) {
      return _.each(this.list, iterator, context);
    },

    find: function(finder) {
      return _.find(this.list, finder);
    },

    findById: function(id) {
      return this.find(function(view) {
        return id === view.model.id;
      });
    },

    findByEl: function(el) {
      return this.find(function(view) {
        return el === view.el;
      });
    }
  });


  /**
   * The NodeView provides an interface to the node.  It will also create a
   * ContentView for the node's content.  Additionally, it will create child
   * NodeViews for all of the nodes in children.
   *
   * Properties:
   *
   * -  `this.model` is the node.
   * -  `this.collection` is the node's children (Also available in
   *    `this.model.children`.
   * -  `this.app` is the instance of AppView
   */
  var NodeView = Widgy.View.extend({
    className: 'node',
    template: 'node_view',
    
    events: {
      'mousedown .drag_handle': 'startDrag',
      'mouseup .node_drag_placeholder': 'dropChildView'
    },

    initialize: function(options) {
      _.bindAll(this,
        'addAll',
        'addOne',
        'startDrag',
        'followMouse',
        'stopDrag',
        'becomeDropTarget',
        'dropChildView',
        'reposition',
        'setPlaceholders',
        'clearPlaceholders'
      );

      this.collection
        .on('reset', this.addAll)
        .on('add', this.addOne);

      this.model
        .on('remove', this.close)
        .on('change', this.reposition);

      this.app = options.app;

      this.app.node_view_list.push(this);
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(node) {
      var node_view = new NodeView({
        model: node,
        collection: node.children,
        app: this.app
      });

      this.bindChildViewEvents(node_view);

      this.$children.append(node_view.render().el);
    },

    /**
     * `startDrag`, `stopDrag`, `followMouse`, and `reposition` all deal with a
     * NodeView itself being dragged around.
     */
    startDrag: function(event) {
      event.preventDefault();
      event.stopPropagation();

      this.app.startDrag(this);

      // hide placeholder behind me.
      this.$el.prev().hide();
      this.clearPlaceholders();

      // TODO: this should probably call this.app.stopDrag.  (Investigate)
      // TODO: should a NodeView know about the document?  I would prefer it if
      // views only knew about their subviews.  Not about anything above them.
      $(document).on('mouseup.' + this.cid, this.stopDrag);
      // TODO: store internal offset so as to know where on the drag handle I
      // started dragging.
      $(document).on('mousemove.' + this.cid, this.followMouse);
      // TODO: follow mouse on scroll.
      this.followMouse(event);

      this.$el.addClass('being_dragged');
    },

    stopDrag: function() {
      this.$el.css({
        position: 'static'
      });

      $(document).off('.' + this.cid);

      this.trigger('stopDrag', this);
      this.$el.removeClass('being_dragged');
    },

    followMouse: function(event) {
      this.$el.css({
        position: 'absolute',
        top: event.pageY,
        left: event.pageX
      });
    },

    /**
     * This method puts the NodeView in the correct spot after a model change.
     */
    reposition: function(model, options) {
      if ( model.get('left_id') ) {
        if ( model.get('left_id') === model.id )
          return;

        var left_view = this.app.node_view_list.findById(model.get('left_id'));
        left_view.$el.after(this.el);
      } else {
        var parent_view = this.app.node_view_list.findById(model.get('parent_id'));
        parent_view.$children.prepend(this.el);
      }
      // TODO: fix collections and stuff.
    },

    /**
     * `bindChildViewEvents`, `becomeDropTarget`, `dropChildView`,
     * `setPlaceholders`, and `clearPlaceholders` all deal with a different
     * NodeView being dragged.  It is confusing that these methods are on the
     * same class that the methods dealing with being dragged around are on,
     * but that's the nature of the beast with recursive nodes.
     */
    bindChildViewEvents: function(child_view) {
      child_view.on('stopDrag', this.clearPlaceholders);
    },

    becomeDropTarget: function() {
      this.setPlaceholders();
    },

    /**
     * This is the method that is called when the NodeView that is being
     * dragged is dropped one of my placeholders.
     */
    dropChildView: function(event) {
      event.preventDefault();
      // The document is also listening to the event that triggers this method.
      // We need to ensure that bubbling stops here.
      event.stopPropagation();

      var $children = this.$children;
      var index = $(event.target).index() / 2;

      // We need to stop the drag before finding the left node.
      // `this.app.stopDrag` will clear all of the placeholders, so we need to
      // remove them before we can get elements by index.
      var dragged_view = this.app.stopDrag();

      var left_id = null;

      // If index is 0 there is no left element and we want to set
      // it to null.
      if ( index !== 0 ) {
        var left_el = $children.children().eq(index - 1)[0],
            left_view = this.app.node_view_list.findByEl(left_el);

        left_id = left_view.model.id;
      }

      // pessimistic save (for now).
      dragged_view.model.save({
        parent_id: this.model.id,
        left_id: left_id
      }, {wait: true});
    },

    // TODO: Placeholder probably should be its own view, that way we can put
    // thing inside of it.
    setPlaceholders: function() {
      var $children = this.$children,
          $placeholder = this.renderTemplate('node_drag_placeholder');

      $children.prepend($placeholder);
      $children.children('.node').each(function(index, elem) {
        $(elem).after($placeholder.clone());
      });
    },

    clearPlaceholders: function() {
      this.$children.find('.node_drag_placeholder')
        .unbind()
        .remove();
    },

    render: function() {
      Widgy.View.prototype.render.apply(this, arguments);

      var content = this.model.content,
          view_class = content.getViewClass();

      this.content_view = new view_class({
        model: content
      });

      this.$content = this.$('.content:first');
      this.$content.append(this.content_view.render().el);

      this.$children = this.$('.children:first');

      // TODO: investigate possible problems with this.
      this.addAll();

      return this;
    }
  });


  _.extend(exports, {
    Node: Node,
    NodeCollection: NodeCollection,
    NodeView: NodeView,
    NodeViewList: NodeViewList
  });

})(this.Widgy);
