define([ 'jquery', 'widgy.backbone', 'widgy.contents',
    'text!nodes/node_view.html',
    'text!nodes/placeholder.html',
    ], function($, Backbone, contents,
      node_view_template,
      placeholder_template
      ) {

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
      Backbone.Model.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'instantiateContent'
        );
      // content gets set because it is in the JSON for the node.  We need to
      // unset it as it is not an attribute, but a property.  We also need to
      // instantiate it as a real Content Model.
      this._content = this.get('content');
      this.unset('content');

      contents.getModel(this._content.__module_name__, this.instantiateContent);

      // same as content.  We need to actually instantiate the NodeCollection
      // and set it as a property, not an attribute.
      var children = this.get('children');
      this.children = new NodeCollection(children);
      this.unset('children');
    },

    instantiateContent: function(model_class) {
      this.content = new model_class(this._content);
      delete this._content;

      this.trigger('loaded:content', this.content);
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
   * -  `this.model` is the node.
   * -  `this.collection` is the node's children (Also available in
   *    `this.model.children`.
   * -  `this.app` is the instance of AppView
   */
  var NodeView = Backbone.View.extend({
    className: 'node',
    template: node_view_template,
    
    events: {
      'mousedown .drag_handle': 'startDrag',
      'mouseup .node_drag_placeholder': 'dropChildView'
    },

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);
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

      this.model.bind('loaded:content', this.render);
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

      this.$children.append(node_view.el);
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

      // follow mouse real quick, don't wait for mousemove.
      this.followMouse(event);

      this.$el.addClass('being_dragged');
    },

    stopDrag: function() {
      this.$el.css({
        position: 'static'
      });

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
     * `becomeDropTarget`, `dropChildView`, `setPlaceholders`, and
     * `clearPlaceholders` all deal with a different NodeView being dragged.
     * It is confusing that these methods are on the same class that the
     * methods dealing with being dragged around are on, but that's the nature
     * of the beast with recursive nodes.
     */
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
          $placeholder = this.renderTemplate(placeholder_template);

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

    render: function(content) {
      Backbone.View.prototype.render.apply(this, arguments);

      var view_class = content.getViewClass();

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


  return {
    Node: Node,
    NodeCollection: NodeCollection,
    NodeView: NodeView
  };

});
