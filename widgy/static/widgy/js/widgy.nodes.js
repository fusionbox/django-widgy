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


  function NodeViewList() {
    this.list = []
  }

  _.extend(NodeViewList.prototype, {
    push: function(view) {
      this.list.push(view);
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

  var node_view_list = new NodeViewList;

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
   */
  var NodeView = Widgy.View.extend({
    className: 'node',
    template: 'node_view',
    
    events: {
      'click .drag_handle': 'startDrag',
      'click .node_drag_placeholder': 'stopChildDrag'
    },

    initialize: function() {
      _.bindAll(this,
        'addAll',
        'addOne',
        'startDrag',
        'stopDrag',
        'startChildDrag',
        'stopChildDrag',
        'reposition'
      );

      this.collection
        .on('reset', this.addAll)
        .on('add', this.addOne);

      this.model
        .on('remove', this.close)
        .on('change', this.reposition);

      node_view_list.push(this);
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(node) {
      var node_view = new NodeView({
        model: node,
        collection: node.children
      });

      this.bindChildViewEvents(node_view);

      this.$children.append(node_view.render().el);
    },

    startDrag: function(event) {
      event.preventDefault();
      // TODO: don't stop propagation
      event.stopPropagation();

      this.$el.addClass('being_dragged');
      this.trigger('startDrag', this);
    },

    stopDrag: function() {
      this.$el.removeClass('being_dragged');
    },

    stopChildDrag: function(event) {
      event.preventDefault();
      event.stopPropagation();

      var $children = this.$children;
      var index = $(event.target).index() / 2;

      this.clearPlaceholders();

      var left_id = null;

      // If index is 0 there is no left element and we want to set
      // it to null.
      if ( index !== 0 ) {
        var left_el = $children.children().eq(index - 1)[0],
            left_view = node_view_list.findByEl(left_el);

        left_id = left_view.model.id;
      }

      this.dragged_view.model.save({
        parent_id: this.model.id,
        left_id: left_id
      });

      this.dragged_view.stopDrag();
      delete this.dragged_view;
    },

    bindChildViewEvents: function(child_view) {
      child_view.on('startDrag', this.startChildDrag);
    },

    startChildDrag: function(child_view) {
      var $children = this.$children,
          $placeholder = this.renderTemplate('node_drag_placeholder');

      $children.prepend($placeholder);
      $children.children('.node').each(function(index, elem) {
        $(elem).after($placeholder.clone());
      });

      this.dragged_view = child_view;
    },

    clearPlaceholders: function() {
      this.$children.find('.node_drag_placeholder')
        .unbind()
        .remove();
    },

    reposition: function(model, options) {
      if ( model.get('left_id') ) {
        if ( model.get('left_id') === model.id )
          return;

        var left_view = node_view_list.findById(model.get('left_id'));
        left_view.$el.after(this.el);
      } else {
        var parent_view = node_view_list.findById(model.get('parent_id'));
        parent_view.$children.prepend(this.el);
      }
      // TODO: fix collections and stuff.
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
    NodeView: NodeView
  });

})(this.Widgy);
