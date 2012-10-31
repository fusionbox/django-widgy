define([ 'exports', 'jquery', 'underscore', 'widgy.backbone', 'widgy.contents', 'shelves/shelves',
    'text!./node.html',
    'text!./preview.html',
    'text!./drop_target.html'
    ], function(exports, $, _, Backbone, contents, shelves,
      node_view_template,
      node_preview_view_template,
      drop_target_view_template
      ) {

  window.debug = function(where) {
    if ( debug[where] ) {
      debugger;
    } else {
      console.log(where, this, _.rest(arguments));
    }
  };

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

      this
        .on('change:content', this.loadContent);

      // same as content.  We need to actually instantiate the NodeCollection
      // and set it as a property, not an attribute.
      var children = this.get('children');
      this.children = new NodeCollection(children);
      this.unset('children');
    },

    url: function() {
      if ( this.id ) {
        return this.id;
      }
      return this.urlRoot;
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
        // This is asynchronous because of requirejs.
        contents.getModel(content.component, _.bind(this.instantiateContent, this, content));
      }
    },

    instantiateContent: function(content, model_class) {
      this.content = new model_class(content);

      // content gets set because it is in the JSON for the node.  We need to
      // unset it as it is not an attribute, but a property.  We also need to
      // instantiate it as a real Content Model.
      this.unset('content');

      this.trigger('load:content', this.content);
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
    tagName: 'li',
    className: 'node',
    
    events: {
      'mousedown .drag_handle': 'startBeingDragged'
    },

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'startBeingDragged',
        'followMouse',
        'stopBeingDragged',
        'checkDidReposition',
        'reposition',
        'addDropTargets',
        'clearDropTargets'
      );

      this.model
        .on('remove', this.close)
        .on('destroy', this.close)
        .on('reposition', this.reposition);

      this.app = options.app;

      this.drop_targets_list = new Backbone.ViewList;
    },

    /*
     * Make sure this happens after model sync.  We need to have the
     * updated data.
     */
    checkDidReposition: function(model, resp, options) {
      debug('checkDidReposition');

      var changed = model.hasChanged('parent_id'),
          new_right_id = model.get('right_id'),
          old_right_id,
          right_view;

      if ( ! changed ) {
        right_view = this.app.node_view_list.findByEl(this.$el.next()[0]);

        if ( right_view ) {
          old_right_id = right_view.model.id;
        } else {
          old_right_id = null;
        }

        changed = old_right_id !== new_right_id;
      }

      if ( changed ) {
        this.triggerReposition(model);
      }
    },

    triggerReposition: function(model) {
      model.trigger('reposition', model, model.get('parent_id'), model.get('right_id'));
    },

    /**
     * `startBeingDragged`, `stopBeingDragged`, `followMouse`, and `reposition` all deal with a
     * NodeView itself being dragged around.
     */
    startBeingDragged: function(event) {
      // only on a left click.
      if ( event.button !== 0 )
        return;

      event.preventDefault();
      event.stopPropagation();

      // Store the mouse offset in this container for followMouse to use.  We
      // need to get this before `this.app.startDrag`, otherwise the drop
      // targets screw everything up.
      var offset = this.$el.offset();
      this.cursorOffsetX = event.clientX - offset.left + (event.pageX - event.clientX);
      this.cursorOffsetY = event.clientY - offset.top + (event.pageY - event.clientY);

      // follow mouse really quick, just in case they haven't moved their mouse
      // yet.
      this.followMouse(event);

      this.trigger('startDrag', this);

      this.$el.addClass('being_dragged');
    },

    stopBeingDragged: function() {
      this.$el.css({
        top: 0,
        left: 0
      });

      this.$el.removeClass('being_dragged');
    },

    followMouse: function(mouse) {
      this.$el.css({
        top: (mouse.clientY - this.cursorOffsetY),
        left: (mouse.clientX - this.cursorOffsetX)
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
        'receiveChildView',
        'renderContent'
        );

      this.model
        .on('load:content', this.renderContent);

      this.collection = this.model.children;

      this.collection
        .on('reset', this.addAll)
        .on('add', this.addOne);

      this.list = new Backbone.ViewList;
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(node) {
      var node_view = new NodeView({
        model: node,
        app: this.app
      });

      node_view.on('all', this.bubble);

      this.list.push(node_view);
      this.trigger('created', node_view);

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
    addDropTargets: function(view) {
      var $children = this.$children,
          that = this,
          mine = this.list.contains(view);

      // do nothing if it's me or I'm not accepting children.
      if ( this === view ||
          (! mine && this.model.content && !this.model.content.get('accepting_children')) )
      {
        return;
      }

      $children.prepend(this.createDropTarget().el);
      $children.children('.node').each(function(index, elem) {
        var drop_target = that.createDropTarget().$el.insertAfter(elem);

        if ( mine && view.el == elem )
          drop_target.hide();
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
          right_view = this.list.findById(right_id);
          right_view.$el.before(child_node_view.el);
      } else {
        this.$children.append(child_node_view.el);
      }
    },


    dropChildView: function(drop_target) {
      var index = drop_target.$el.index() / 2;

      // We need to stop the drag before finding the right node.
      // `this.app.stopDrag` will clear all of the drop targets, so we need to
      // remove them before we can get elements by index.
      this.trigger('stopDrag', index, this.receiveChildView);
    },

    /**
     * This is the method that is called when the NodeView that is being
     * dragged is dropped on one of my drop targets.
     */
    receiveChildView: function(dragged_view, index) {
      var $children = this.$children,
          right_id = null,
          attributes = {
            parent_id: this.model.id,
            right_id: null,
          };

      // If index is the length of $children.children there is no right element
      // and we want it set to null.  Otherwise there is a right and we need
      // its id.
      //
      // ($children.children() refers to DOM elements.)
      if ( index !== $children.children().length ) {
        var right_el = $children.children().eq(index)[0],
            right_view = this.list.findByEl(right_el);

        // Dragged into its own drop target.
        if ( dragged_view === right_view )
          return;

        attributes.right_id = right_view.model.id;
      }

      // pessimistic save (for now).
      debug('receiveChildView', dragged_view, attributes);
      dragged_view.model.save(attributes, {
        wait: true,
        success: dragged_view.checkDidReposition
      });
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);

      this.$children = this.$el.children('.node_children');
      this.$content = this.$el.children('.content');

      // TODO: this could be like a document.ready sorta?
      this.model.checkIsContentLoaded();

      // TODO: investigate possible problems with this.
      this.addAll();

      return this;
    },

    renderContent: function(content) {
      var view_class = content.getViewClass();

      content_view = new view_class({
        model: content,
        el: this.$content
      });
      
      content_view.render();

      if ( ! this.model.get('parent_id') || content.get('shelf') )
      {
        this.renderShelf();
      }
    },

    renderShelf: function() {
      var shelf_view = this.shelf_view = new shelves.ShelfView({
        collection: new shelves.ShelfCollection({
            node: this.model
          }),
        app: this.app
      });

      shelf_view.on('all', this.bubble);
      shelf_view.collection.fetch();

      this.$el.append(shelf_view.render().el);
    },

    toJSON: function() {
      var json = this.model.toJSON();
      if ( this.model.content )
        json.content = this.model.content.toJSON();

      return json;
    }
  });


  var NodePreviewView = NodeViewBase.extend({
    template: node_preview_view_template
  });


  var DropTargetView = Backbone.View.extend({
    tagName: 'li',
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


  _.extend(exports, {
    DropTargetView: DropTargetView,
    Node: Node,
    NodeCollection: NodeCollection,
    NodeView: NodeView,
    NodePreviewView: NodePreviewView,
    NodeViewBase: NodeViewBase
  });

});
