define([ 'jquery', 'underscore', 'widgy.backbone', 'widgy.contents',
    'text!./node.html',
    'text!./preview.html',
    'text!./drop_target.html'
    ], function($, _, Backbone, contents,
      node_view_template,
      node_preview_view_template,
      drop_target_view_template
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
        'instantiateContent',
        'checkDidReposition'
        );

      this
        .on('change', this.checkDidReposition)
        .on('change:content', this.loadContent);

      // same as content.  We need to actually instantiate the NodeCollection
      // and set it as a property, not an attribute.
      var children = this.get('children');
      this.children = new NodeCollection(children);
      this.unset('children');
    },

    checkDidReposition: function() {
      if ( this.hasChanged('parent_id') ||
          (this.hasChanged('right_id') && this.id !== this.get('right_id')) )
      {
        this.trigger('reposition', this, this.get('parent_id'), this.get('right_id'));
      }
    },

    checkIsContentLoaded: function() {
      if ( this.content && this.content instanceof contents.Content ) {
        this.trigger('load:content', this.content);
      } else {
        this.loadContent(this, this.get('content'));
      }
    },

    loadContent: function(model, content) {
      if ( content )
      {
        // content gets set because it is in the JSON for the node.  We need to
        // unset it as it is not an attribute, but a property.  We also need to
        // instantiate it as a real Content Model.
        this.unset('content');

        // This is asynchronous because of requirejs.
        contents.getModel(content.__class__, _.bind(this.instantiateContent, this, content));
      }
    },

    instantiateContent: function(content, model_class) {
      this.content = new model_class(content);

      this.trigger('load:content', this.content);
    },

    toJSON: function() {
      var json = Backbone.Model.prototype.toJSON.apply(this, arguments);
      if ( this.content )
        json.content = this.content.toJSON();
      return json;
    }

  });


  /**
   * NodeCollections provide the children interface for nodes and also an
   * interface to NodeViews for how to handle child NodeViews.
   */
  var NodeCollection = Backbone.Collection.extend({
    model: Node
  });


  /**
   * Provides an interface for a draggable NodeView.  See NodeView for more
   * specific Node functionality related definition.  NodeViewBase is exposed
   * for subclassing by a NodePreviewView and NodeView.
   *
   * TODO: Does NodePreviewView do anything that NodeViewBase doesn't?
   */
  var NodeViewBase = Backbone.View.extend({
    className: 'node',
    
    events: {
      'mousedown .drag_handle': 'startDrag'
    },

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'startDrag',
        'afterStartDrag',
        'followMouse',
        'stopDrag',
        'reposition',
        'addDropTargets',
        'clearDropTargets'
      );

      this.model
        .on('remove', this.close)
        .on('destroy', this.close)
        .on('reposition', this.reposition);

      this.app = options.app;
      this.app.node_view_list.push(this);

      this.drop_targets_list = new Backbone.ViewList;
    },

    /**
     * `startDrag`, `stopDrag`, `followMouse`, and `reposition` all deal with a
     * NodeView itself being dragged around.
     */
    startDrag: function(event) {
      // only on a left click.
      if ( event.button !== 0 )
        return;

      event.preventDefault();
      event.stopPropagation();

      this.app.startDrag(this);
      this.afterStartDrag();

      // Store the mouse offset in this container for followMouse to
      // use.
      this.offsetY = event.offsetY;
      this.offsetX = event.offsetX;

      // follow mouse really quick, just in case they haven't moved their mouse
      // yet.
      this.followMouse(event);

      this.$el.addClass('being_dragged');
    },

    /**
     * Hook called when a node is starting to be dragged.
     */
    afterStartDrag: function() {},

    stopDrag: function() {
      this.$el.css({
        position: 'static'
      });

      this.$el.removeClass('being_dragged');
    },

    followMouse: function(event) {
      this.$el.css({
        position: 'absolute',
        top: event.pageY - this.offsetY,
        left: event.pageX - this.offsetX
      });
    },

    /**
     * If the node has been put into a different parent, we need to update the
     * collection.  That parent will be listening for adding and it will handle
     * the positioning.  Otherwise, this node is still in the right parent and
     * it just needs to be positioned in the parent.
     *
     * This is a callback to the reposition event on the Node model.
     *
     * When a Node is removed from the Collection, it closes this, but we need
     * to clean up our bindings.
     */
    reposition: function(model, parent_id, right_id) {
      var parent_view = this.app.node_view_list.findById(parent_id);

      // This line is a little confusing.  For a model, the
      // `collection` property is its parent collection, for a view,
      // the `collection` is a child.  If a model has the same
      // `collection` as a view, that means the view is the parent
      // of the model.
      if ( model.collection !== parent_view.collection ) {
        model.collection.remove(model);
        this.model.off('reposition', this.reposition);
        parent_view.collection.add(model);
      } else {
        parent_view.position(this);
      }
    },

    /**
     * `addDropTargets` and `clearDropTargets` are required as an API for the
     * AppView. See NodeView for the actual implementation.
     */
    addDropTargets: function() {},
    clearDropTargets: function() {}
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
  var NodeView = NodeViewBase.extend({
    template: node_view_template,

    events: function() {
      return _.extend({}, NodeViewBase.prototype.events , {
        'click .delete': 'delete'
      });
    },

    initialize: function() {
      NodeViewBase.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'addAll',
        'addOne',
        'position',
        'createDropTarget',
        'dropChildView',
        'renderContent'
        );

      this.model
        .on('load:content', this.renderContent);

      this.collection = this.model.children;

      this.collection
        .on('reset', this.addAll)
        .on('add', this.addOne);
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(node) {
      var node_view = new NodeView({
        model: node,
        app: this.app
      });

      this.position(node_view.render());
    },

    'delete': function(event) {
      event.stopPropagation();
      this.model.destroy();
    },

    /**
     * `addDropTargets`, `createDropTarget`, `clearDropTargets`, `position`,
     * and `dropChildView` all deal with a possible child NodeView being
     * dragged.  It is confusing that these methods are on the same class that
     * the methods dealing with being dragged around are on, but that's the
     * nature of the beast with recursive nodes.
     */
    addDropTargets: function() {
      var $children = this.$children,
          that = this;

      if ( this.model.content && !this.model.content.get('accepting_children') )
      {
        return;
      }

      $children.prepend(this.createDropTarget().el);
      $children.children('.node').each(function(index, elem) {
        $(elem).after(that.createDropTarget().el);
      });
    },

    createDropTarget: function() {
      var drop_target = new DropTargetView;
      drop_target.on('dropped', this.dropChildView);
      this.drop_targets_list.push(drop_target);

      return drop_target.render();
    },

    clearDropTargets: function() {
      this.drop_targets_list.closeAll();
    },

    position: function(child_node_view) {
      var child_node = child_node_view.model;

      if ( child_node.get('right_id') ) {
        var right_id = child_node.get('right_id'),
          right_view = this.app.node_view_list.findById(right_id);
          right_view.$el.before(child_node_view.el);
      } else {
        this.$children.append(child_node_view.el);
      }
    },

    /**
     * This is the method that is called when the NodeView that is being
     * dragged is dropped on one of my drop targets.
     */
    dropChildView: function(view) {
      var $children = this.$children;
      var index = view.$el.index() / 2;

      // We need to stop the drag before finding the right node.
      // `this.app.stopDrag` will clear all of the drop targets, so we need to
      // remove them before we can get elements by index.
      var dragged_view = this.app.stopDrag();

      var right_id = null;

      // If index is the length of $children.children there is no right element
      // and we want it set to null.  Otherwise there is a right and we need
      // its id.
      //
      // ($children.children() refers to DOM elements.)
      if ( index !== $children.children().length ) {
        var right_el = $children.children().eq(index)[0],
            right_view = this.app.node_view_list.findByEl(right_el);

        right_id = right_view.model.id;
      }

      // Dragged into my own drop target.
      if ( dragged_view === right_view )
        return;

      // pessimistic save (for now).
      dragged_view.model.save({
        parent_id: this.model.id,
        right_id: right_id
      }, {wait: true});
    },

    afterStartDrag: function() {
      // hide drop target behind me.
      this.$el.next().hide();
      this.clearDropTargets();
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);

      this.$children = this.$('.children:first');
      this.$content = this.$('.content:first');

      // TODO: this could be like a document.ready sorta?
      this.model.checkIsContentLoaded();

      // TODO: investigate possible problems with this.
      this.addAll();

      return this;
    },

    renderContent: function(content) {
      var view_class = content.getViewClass();

      content_view = new view_class({
        model: content
      });

      this.$content.html(content_view.render().el);
    }
  });


  var NodePreviewView = NodeViewBase.extend({
    tagName: 'li',
    template: node_preview_view_template
  });


  var DropTargetView = Backbone.View.extend({
    className: 'node_drop_target',

    template: drop_target_view_template,

    triggers: {
      'mouseup': 'dropped'
    },

    events: {
      'mouseenter': 'activate',
      'mouseleave': 'deactivate'
    },

    activate: function(event) {
      this.$el.addClass('active');
    },

    deactivate: function(event) {
      this.$el.removeClass('active');
    }
  });


  return {
    DropTargetView: DropTargetView,
    Node: Node,
    NodeCollection: NodeCollection,
    NodeView: NodeView,
    NodePreviewView: NodePreviewView,
    NodeViewBase: NodeViewBase
  };

});
