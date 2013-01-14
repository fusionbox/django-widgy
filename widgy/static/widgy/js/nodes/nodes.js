define([ 'exports', 'jquery', 'underscore', 'widgy.backbone', 'widgy.contents', 'shelves/shelves', 'modal/modal',
    'text!./node.html',
    'text!./preview.html',
    'text!./drop_target.html',
    'text!./popped_out.html'
    ], function(exports, $, _, Backbone, contents, shelves, modal,
      node_view_template,
      node_preview_view_template,
      drop_target_view_template,
      popped_out_template
      ) {

  var debug = function(where) {
    console.log(where, this, _.rest(arguments));
  };

  /**
   * Nodes provide structure in the tree.  Nodes only hold data that deals with
   * structure.  Any other data lives in its content.
   *
   * A node will have two properties: `children` and `content`.  `children` is
   * a NodeCollection which is basically just a list of child nodes. `content`
   * is model containing all non-structure information about a node.  The
   * actual Model Class that defines the content property depends on the
   * content type.  See `widgy.contents.js` for more information.
   */
  var Node = Backbone.Model.extend({
    urlRoot: '/admin/widgy/node/',

    constructor: function(attrs, options) {
      this.children = new NodeCollection();

      Backbone.Model.call(this, attrs, options);
    },

    initialize: function() {
      Backbone.Model.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'instantiateContent'
        );
    },

    set: function(key, val, options) {
      var attr, attrs;

      // Handle both `"key", value` and `{key: value}` -style arguments.
      if (_.isObject(key)) {
        attrs = key;
        options = val;
      } else {
        (attrs = {})[key] = val;
      }

      var children = attrs.children,
          content = attrs.content;

      delete attrs.children;
      delete attrs.content;

      var ret = Backbone.Model.prototype.set.call(this, attrs, options);

      if (ret) {
        if (children) this.children.update(children);
        if (content) this.loadContent(content);
      }

      return ret;
    },

    url: function() {
      if ( this.id ) {
        return this.id;
      }
      return this.urlRoot;
    },

    loadContent: function(content) {
      debug.call(this, 'loadContent', content);
      if ( content ) {
        // This is asynchronous because of requirejs.
        contents.getModel(content.component, _.bind(this.instantiateContent, this, content));
      }
    },

    instantiateContent: function(content, model_class) {
      debug.call(this, 'instantiateContent', content, model_class);

      this.content = new model_class(content, {
        node: this
      });

      this.trigger('load:content', this.content);
    },

    sync: function(method, model, options) {
      debug.call(this, 'Node#sync', arguments);
      Backbone.sync.apply(this, arguments);

      if (!options.silent)
        this.trigger('node:sync', this);
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

      this
        .listenTo(this.model, 'destroy', this.close)
        .listenTo(this.model, 'remove', this.close)
        .listenTo(this.model, 'reposition', this.reposition);

      this.app = options.app;
      this.parent = options.parent;
    },

    checkDidReposition: function(model, resp, options) {
      debug('checkDidReposition');

      var new_parent_id = model.get('parent_id'),
          old_parent_id = null,
          new_right_id = model.get('right_id'),
          old_right_id = null,
          right_view = this.app.node_view_list.findByEl(this.$el.next()[0]),
          parent_view = this.app.node_view_list.findByEl(this.$el.parents('.node')[0]);


      if ( parent_view ) {
        old_parent_id = parent_view.model.id;
      }

      if ( right_view ) {
        old_right_id = right_view.model.id;
      }

      if ( old_right_id !== new_right_id || old_parent_id !== new_parent_id ) {
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
      event.preventDefault();
      event.stopPropagation();

      // only on a left click.
      if ( event.which !== 1 )
        return;

      // Store the mouse offset in this container for followMouse to use.  We
      // need to get this before `this.app.startDrag`, otherwise the drop
      // targets screw everything up.
      var offset = this.$el.offset();
      this.cursorOffsetX = event.clientX - offset.left + (event.pageX - event.clientX);
      this.cursorOffsetY = event.clientY - offset.top + (event.pageY - event.clientY);

      // follow mouse really quick, just in case they haven't moved their mouse
      // yet.
      this.followMouse(event);

      this.$el.addClass('being_dragged');

      this.trigger('startDrag', this);
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
        'click .delete': 'delete',
        'click .pop_out': 'popOut',
        'click .pop_in': 'popIn'
      });
    },

    initialize: function() {
      NodeViewBase.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'renderChildren',
        'addChild',
        'position',
        'createDropTarget',
        'startDrag',
        'stopDrag',
        'stopDragging',
        'dropChildView',
        'receiveChildView',
        'renderContent',
        'nodeSync',
        'popOut',
        'popIn'
        );

      this.collection = this.model.children;
      this.drop_targets_list = new Backbone.ViewList();

      this
        .listenTo(this.model, 'load:content', this.renderContent)
        .listenTo(this.model, 'node:sync', this.nodeSync)
        .listenTo(this.collection, 'add', this.addChild)
        .listenTo(this.collection, 'reset', this.renderChildren);

      this.list = new Backbone.ViewList();
    },

    onClose: function() {
      NodeViewBase.prototype.onClose.apply(this, arguments);

      this.list.closeAll();
    },

    renderChildren: function() {
      debug.call(this, 'renderChildren');

      this.list.closeAll();
      this.collection.each(this.addChild);
    },

    addChild: function(node) {
      var node_view = new NodeView({
        model: node,
        parent: this,
        app: this.app
      });

      this
        .listenTo(node_view, 'startDrag', this.startDrag)
        .listenTo(node_view, 'stopDrag', this.stopDrag)
        .listenTo(node_view, 'node:sync', this.nodeSync);

      this.app.node_view_list.push(node_view);
      this.list.push(node_view);
      this.position(node_view.render());
    },

    'delete': function(event) {
      this.model.destroy();
      return false;
    },

    startDrag: function(dragged_view) {
      debug.call(this, 'startDrag', dragged_view);

      if ( ( this.hasShelf() && ! dragged_view.model.id || ! this.model.get('parent_id') )) {
        this.dragged_view = dragged_view;

        $(document).on('mouseup.' + dragged_view.cid, this.stopDragging);
        $(document).on('mousemove.' + dragged_view.cid, dragged_view.followMouse);
        $(document).on('selectstart.' + dragged_view.cid, function(){ return false; });

        this.addDropTargets(dragged_view);
      } else {
        // propagate event
        this.trigger('startDrag', dragged_view);
      }
    },

    stopDragging: function() {
      var dragged_view = this.dragged_view;
      delete this.dragged_view;

      $(document).off('.' + dragged_view.cid);

      this.clearDropTargets();

      dragged_view.stopBeingDragged();

      return dragged_view;
    },

    /**
     * `nodeSync` allows us to refresh the shelf every time a node is moved or
     * deleted.  It doesn't refresh the shelf every time a new node is created,
     * but that is already handled by the shelf.  That would work only if the
     * events from preview nodes bubbled up through the shelf and hit the
     * NodeViews that are already in the tree.  If this node doesn't have a
     * shelf, it will just bubble the event.
     */
    nodeSync: function(node) {
      debug.call(this, 'nodeSync', node);

      if ( this.hasShelf() && node !== this.model ) {
        this.shelf.refresh();
      } else {
        this.trigger('node:sync', node);
      }
    },

    stopDrag: function(callback) {
      debug.call(this, 'stopDrag', callback);

      if ( this.hasShelf() && this.dragged_view ) {
        callback(this.stopDragging());
      } else {
        // propagate event
        this.trigger('stopDrag', callback);
      }
    },

    getShelf: function() {
      if ( this.hasShelf() )
        return this.shelf;
      else
        return this.parent.getShelf();
    },

    canAcceptChild: function(view) {
      if ( view instanceof NodePreviewView ) {
        return _.contains(view.model.get('possible_parent_nodes'), this.model.id)
      } else {
        // it is me.
        if ( this === view )
          return false;

        // it is already my child.
        if ( this.list.contains(view) )
          return true;

        return this.getShelf().validParentOf(
            this.model.id,
            view.model.content.get('__class__')
            );
      }
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

      // I can't be my own grandfather.
      if (this !== view) {
        this.list.each(function(node_view) {
          node_view.addDropTargets(view);
        });
      }

      if (this.canAcceptChild(view))
      {
        $children.prepend(this.createDropTarget().el);
        $children.children('.node').each(function(index, elem) {
          var drop_target = that.createDropTarget().$el.insertAfter(elem);

          if ( mine && view.el == elem )
            drop_target.hide();
        });
      }
    },

    createDropTarget: function() {
      var drop_target = new DropTargetView();
      drop_target.on('dropped', this.dropChildView);
      this.drop_targets_list.push(drop_target);

      return drop_target.render();
    },

    clearDropTargets: function() {
      this.drop_targets_list.closeAll();

      this.list.each(function(node_view) {
        node_view.clearDropTargets();
      });
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
      var index = drop_target.$el.index() / 2,
          dragCallback = _.bind(this.receiveChildView, this, index);

      // We need to stop the drag before finding the right node.
      // `this.app.stopDrag` will clear all of the drop targets, so we need to
      // remove them before we can get elements by index.
      this.stopDrag(dragCallback);
    },

    /**
     * This is the method that is called when the NodeView that is being
     * dragged is dropped on one of my drop targets.
     */
    receiveChildView: function(index, dragged_view) {
      debug('receiveChildView');

      var $children = this.$children,
          attributes = {
            parent_id: this.model.id,
            right_id: null
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

      dragged_view.model.save(attributes, {
        success: dragged_view.checkDidReposition,
        error: modal.raiseError
      });
    },

    hasShelf: function() {
      return this.model.content.get('shelf') || this.options.rootNode;
    },

    render: function() {
      debug.call(this, 'render');
      Backbone.View.prototype.render.apply(this, arguments);

      this.$children = this.$el.children('.node_children');
      this.$content = this.$el.children('.content');

      if ( this.model.content ) {
        this.renderContent(this.model.content);
      }

      this.renderChildren();

      return this;
    },

    renderContent: function(content) {
      debug.call(this, 'renderContent', content);

      var view_class = content.getViewClass();

      content_view = new view_class({
        model: content,
        el: this.$content
      });

      content_view.render();

      if ( content.get('pop_out') == 2 && ! this.options.rootNode )
        return;

      if ( this.hasShelf() ) {
        this.renderShelf();
      }
    },

    renderShelf: function() {
      if (this.shelf) return false;

      var shelf = this.shelf = new shelves.ShelfView({
        collection: new shelves.ShelfCollection({
            node: this.model
          }),
        app: this.app
      });

      this.listenTo(shelf, 'startDrag', this.startDrag);
      shelf.collection.refresh();

      this.$children.before(shelf.render().el);
    },

    toJSON: function() {
      var json = this.model.toJSON();
      if ( this.model.content )
        json.content = this.model.content.toJSON();

      return json;
    },

    popOut: function(event) {
      debug.call(this, 'popOut');

      event.preventDefault();
      event.stopPropagation(); // our parent nodes

      this.subwindow = window.open(event.target.href, '', 'height=500,width=800,resizable=yes,scrollbars=yes');
      this.subwindow.widgyCloseCallback = this.popIn;

      this.collection.reset();
      this.$content.html(this.renderTemplate(popped_out_template, this.toJSON()));
    },

    popIn: function(event) {
      debug.call(this, 'popIn');

      event.preventDefault();
      event.stopPropagation();

      if ( ! this.subwindow.closed ) {
        $(this.subwindow).off('unload', this.popIn);
        this.subwindow.close();
      }

      this.model.fetch();

      return false;
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

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);

      // In a perfect world, the CSS pointer-events property would be supported
      // by all browsers and every version of each browser and we would set
      // pointer-events to none for .node.being_dragged.  But even since we
      // can't use that, we are going to use this method to capture all of the
      // events.
      //
      // Above the drop targets, we put an invisible div that has a z-index
      // high enough to be above the dragged_node.  This allows us to catch the
      // pointer events (mouseup, mouseenter, mouseleave) that we need drop
      // targets to receive.
      //
      // Normally I don't like putting CSS in the JavaScript, but this CSS
      // creates functionality and not prettiness, so I have to.
      this.$el.css({ 'position': 'relative' });

      var $pointerEventsCatcher = $('<div class="pointer_event_catcher">')
        .css({
          'z-index': 1000,
          'opacity': 0,
          'width': '100%',
          'height': '100%',
          'position': 'absolute',
          'top': 0,
          'left': 0
        });
      this.$el.prepend($pointerEventsCatcher);

      return this;
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
