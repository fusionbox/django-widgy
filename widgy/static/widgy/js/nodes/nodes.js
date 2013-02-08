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

    constructor: function() {
      this.children = new NodeCollection(null, {
        parent: this
      });

      Backbone.Model.apply(this, arguments);
    },

    initialize: function() {
      Backbone.Model.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'instantiateContent',
        'trigger'
        );
    },

    parse: function(response) {
      if ( response.node ) {
        return response.node;
      } else {
        return response;
      }
    },

    set: function(key, val, options) {
      var attrs;

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
        if (children) {
          this.children.update2(children, options);
          if ( options && options.resort ) {
            this.children.sortByRight();
          }
        }
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
      if ( this.content ) {
        console.log(this.__class__, 'updating content', content);

        this.content.set(content);
      } else if ( content ) {
        console.log(this.__class__, 'go load my content model');

        // we store these variables because we need them now.
        this.pop_out = content.pop_out;
        this.shelf = content.shelf;
        this.__class__ = content.__class__;
        this.css_classes = content.css_classes;

        // This is asynchronous because of requirejs.
        contents.getModel(content.component, _.bind(this.instantiateContent, this, content));
      }
    },

    instantiateContent: function(content, model_class) {
      console.log(this.__class__, 'instantiating content');

      this.content = new model_class(content, {
        node: this
      });

      this.trigger('load:content', this.content);
    },

    sync: function(method, model, options) {
      debug.call(this, 'Node#sync', arguments);
      // Provides an optimization for refreshing the shelf compatibility.
      // Previously, when editing a node, you had to do two requests (one for
      // the node, one for the shelf compatibility) to update the UI.  In
      // addition, the shelf request had to happen after the node one, to
      // prevent getting the compatibility wrong.  This refreshes compatibility
      // in one request instead of waiting for two round trips.
      var old_success = options.success;

      options.success = function(resp, status, xhr) {
        if ( old_success ) old_success(resp, status, xhr);

        if ( options.app && resp.compatibility ) {
          options.app.setCompatibility(resp.compatibility);
        }
      };

      if ( options.app )
      {
        var model_url = _.result(model, 'url'),
            root_url = _.result(options.app.root_node_view.model, 'url');

        options.url =  model_url + '?include_compatibility_for=' + root_url;
      }

      Backbone.sync.call(this, method, model, options);
    }
  });


  /**
   * NodeCollections provide the children interface for nodes and also an
   * interface to NodeViews for how to handle child NodeViews.
   */
  var NodeCollection = Backbone.Collection.extend({
    model: Node,

    initialize: function(models, options) {
      Backbone.Collection.prototype.initialize.apply(this, arguments);
      this.parent = options.parent;
    },

    /**
     * For each model in the new data, if
     *    - the model exists, update the data of that model.
     *    - the model is new, create a new instance and add it to the
     *      collection.
     *    - else, remove the old model from the collection.
     */
    update2: function(data, options) {
      var models = [];

      _.each(data, function(child) {
        var existing = this.get(child.url);

        if ( existing ) {
          existing.set(child, options);
          models.push(existing);
        } else {
          models.push(child);
        }
      }, this);

      this.update(models, options);
    },

    /**
     * Sort based on the right_ids.  This will most likely fail if the
     * right_ids are not up to date, so please only call this after updating
     * the whole collection.
     */
    sortByRight: function(options) {
      var new_order = [],
          right_id = null;

      while (new_order.length < this.models.length) {
        var has_right = this.where({right_id: right_id})[0];
        new_order.unshift(has_right);

        right_id = has_right.id;
      }

      this.models = new_order;

      if (!options || !options.silent) this.trigger('sort', this, options);
      return this;
    }
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
        'clearDropTargets',
        'canAcceptParent',
        'cssClasses'
      );

      this
        .listenTo(this.model, 'destroy', this.close)
        .listenTo(this.model, 'remove', this.close)
        .listenTo(this.model, 'reposition', this.reposition);

      this.app = options.app;
      this.parent = options.parent;
    },

    triggerReposition: function(model) {
      model.trigger('reposition', model, model.get('parent_id'), model.get('right_id'));
    },

    cssClasses: function() {
      return [];
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);
      _.each(this.cssClasses(), this.$el.addClass, this.$el);

      return this;
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

      if ( ! this.app.ready() )
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

      this.$el.css({
        width: this.$el.width(),
        'z-index': 50
      });
      this.$el.addClass('being_dragged');

      this.trigger('startDrag', this);
    },

    stopBeingDragged: function() {
      this.$el.css({
        top: '',
        left: '',
        width: '',
        'z-index': ''
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
      var new_parent = this.app.node_view_list.findById(parent_id).model,
          new_collection = new_parent.children,
          right, index;

      var getIndex = function() {
        if ( right_id ) {
          right = new_collection.get(right_id);
          index = new_collection.indexOf(right);
        } else {
          index = new_collection.length;
        }
        return index;
      };

      if ( model.collection !== new_collection ) {
        model.collection.remove(model);
        this.model.off('reposition', this.reposition);
        new_collection.add(model, {at: getIndex()});
      } else {
        // remove the model from its old position and insert at new index.
        new_collection.models.splice(new_collection.indexOf(model), 1);
        new_collection.models.splice(getIndex(), 0, model);
      }

      new_collection.trigger('sort');
      new_collection.trigger('position_child');
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
   *    `this.model.children`.)
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
        'createDropTarget',
        'startDrag',
        'stopDrag',
        'stopDragging',
        'dropChildView',
        'receiveChildView',
        'renderContent',
        'resortChildren',
        'popOut',
        'popIn'
        );

      this.collection = this.model.children;
      this.drop_targets_list = new Backbone.ViewList();

      this
        .listenTo(this.model, 'load:content', this.renderContent)
        .listenTo(this.collection, 'add', this.addChild)
        .listenTo(this.collection, 'reset', this.renderChildren)
        .listenTo(this.collection, 'sort', this.resortChildren);

      this.list = new Backbone.ViewList();
    },

    onClose: function() {
      NodeViewBase.prototype.onClose.apply(this, arguments);

      this.content_view.close();
      delete this.content_view;

      this.list.closeAll();
    },

    dontShowChildren: function() {
      return this.model.pop_out === 2 && ! this.options.rootNode;
    },

    renderChildren: function() {
      debug.call(this, 'renderChildren');
      if ( this.dontShowChildren() )
        return;

      this.list.closeAll();
      this.collection.each(this.addChild);
      this.resortChildren();
    },

    addChild: function(node, collection, options) {
      if ( this.dontShowChildren() )
        return;

      var node_view = new NodeView({
        model: node,
        parent: this,
        app: this.app
      });

      this
        .listenTo(node_view, 'startDrag', this.startDrag)
        .listenTo(node_view, 'stopDrag', this.stopDrag);

      this.app.node_view_list.push(node_view);
      if ( options && options.index ) {
        this.list.list.splice(options.index, 0, node_view);
      } else {
        this.list.push(node_view);
      }
      this.$children.append(node_view.render().el);
    },

    resortChildren: function() {
      console.log(this.model.__class__, 'resorting children');
      var new_list = [];
      this.collection.each(function(model) {
        var node_view = this.list.findByModel(model);
        this.$children.append(node_view.el);
        new_list.push(node_view);
      }, this);
      this.list.list = new_list;
    },

    'delete': function(event) {
      var spinner = new Backbone.Spinner({el: this.$content.find('.delete')}),
          model = this.model;

      var error = function() {
        spinner.restore();
        modal.raiseError.apply(this, arguments);
      };

      this.model.collection.trigger('destroy_child');
      this.model.destroy({
        wait: true,
        error: error,
        app: this.app
      });
      return false;
    },

    startDrag: function(dragged_view) {
      debug.call(this, 'startDrag', dragged_view);

      if ( ( this.hasShelf() && ! dragged_view.model.id || ! this.model.get('parent_id') )) {
        this.dragged_view = dragged_view;

        var bindToDocument = _.bind(function() {
          $(document)
            .on('mouseup.' + dragged_view.cid, this.stopDragging)
            .on('mousemove.' + dragged_view.cid, dragged_view.followMouse)
            .on('selectstart.' + dragged_view.cid, function(){ return false; })
            // debugging helper
            .one('keypress.' + dragged_view.cid, function(event) {
              if ( event.which === 96 ) {
                $(document)
                  .off('.' + dragged_view.cid)
                  // resume dragging
                  .one('keypress.' + dragged_view.cid, function(event) {
                    if ( event.which === 96 ) bindToDocument();
                  });
              }
            });
        }, this);

        bindToDocument();

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

      if ( dragged_view.placeholder )
        dragged_view.placeholder.remove();

      this.clearDropTargets();

      dragged_view.stopBeingDragged();

      return dragged_view;
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
      if ( this.model.pop_out == 2 && ! this.options.rootNode )
        return null;
      else if ( this.hasShelf() )
        return this.shelf;
      else
        return this.parent.getShelf();
    },

    canAcceptChild: function(view) {
      return ! this.dontShowChildren() && view.canAcceptParent(this);
    },

    canAcceptParent: function(parent) {
      // it is me.
      if ( this === parent )
        return false;

      // it is already my child.
      if ( parent.list.contains(this) )
        return true;

      return this.app.validateRelationship(parent, this.model.content);
    },

    checkDidReposition: function(model, resp, options) {
      var current_parent_id = model.collection.parent.id,
          current_right = model.collection.at(model.collection.indexOf(model)),
          current_right_id = current_right && current_right.id;

      if ( current_right_id !== model.get('right_id') || current_parent_id !== model.get('parent_id') ) {
        this.triggerReposition(model);
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
        this.list.each(function(node_view) {
          var drop_target = that.createDropTarget().$el.insertAfter(node_view.el);

          if ( mine && view == node_view )
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

      // It's already mine and it was dragged into its own drop target.
      if ( index === this.collection.indexOf(dragged_view) )
        return;

      // This will return the model that we want at our right or undefined.
      var right = this.collection.at(index);

      var attributes = {
        parent_id: this.model.id,
        right_id: right ? right.id : null
      };

      this.collection.trigger('receive_child');
      dragged_view.model.save(attributes, {
        success: dragged_view.checkDidReposition,
        error: modal.raiseError,
        app: this.app
      });
    },

    hasShelf: function() {
      return this.model.shelf || this.options.rootNode;
    },

    render: function() {
      debug.call(this, 'render');
      NodeViewBase.prototype.render.apply(this, arguments);

      this.$children = this.$el.find(' > .widget > .node_children');
      this.$content = this.$el.find(' > .widget > .content ');

      if ( this.model.content ) {
        this.renderContent(this.model.content);
      }

      this.renderChildren();

      if ( this.hasShelf() ) {
        this.renderShelf();
      }

      return this;
    },

    renderContent: function(content) {
      if ( this.content_view )
        return;

      console.log(this.model.__class__, 'renderContent');

      var view_class = content.getViewClass();

      this.content_view = new view_class({
        model: content,
        el: this.$content,
        app: this.app
      });

      this.content_view.render();

      // when we are popped out, we need to remove our own pop out button.
      if ( this.options.rootNode ) {
        this.$content.find('.pop_out').remove();
      }
    },

    renderShelf: function() {
      if (this.shelf)
        return false;

      var shelf = this.shelf = new shelves.ShelfView({
        collection: new shelves.ShelfCollection({
            node: this.model
          }),
        app: this.app
      });

      this.listenTo(shelf, 'startDrag', this.startDrag)
          .listenTo(shelf, 'stopDrag', this.stopDrag);

      // position sticky
      if ( this.options.rootNode ) {
        // The shelf needs to be after the children because in state 0 (fixed),
        // the shelf items will be displayed underneath everything else that is
        // after it in HTML.
        this.$children.after(shelf.render().el);

        var state = -1;
        $(window).scroll(_.bind(function() {
          var upper_bound = this.el.offsetTop,
              lower_bound = upper_bound + this.el.offsetHeight - this.shelf.el.offsetHeight;
          if ( window.scrollY < upper_bound && state !== -1) {
            this.shelf.$el.css({
              position: '',
              top: '',
              left: ''
            });
            state = -1;
          }
          if ( window.scrollY > upper_bound && state !== 0) {
            this.shelf.$el.css({
              position: 'fixed',
              // this 80px is to adjust for Mezzanine's fixed header.
              top: 80,
              left: this.shelf.$el.offset().left
            });
            state = 0;
          }
          if ( window.scrollY > lower_bound && state !== 1) {
            this.shelf.$el.css({
              position: 'absolute',
              top: lower_bound - upper_bound,
              left: ''
            });
            state = 1;
          }
        }, this));
      } else {
        this.$children.before(shelf.render().el);
      }
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

      // If they leave this page, pop back in.
      $(window).on('unload', this.popIn);

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

      this.model.fetch({
        app: this.app,
        resort: true
      });

      return false;
    },

    cssClasses: function() {
      return this.model.css_classes;
    }
  });


  var NodePreviewView = NodeViewBase.extend({
    template: node_preview_view_template,

    // Override the NodeViewBase events, I want the whole thing draggable, not
    // just the drag handle.
    events: {
      'mousedown': 'startBeingDragged'
    },

    checkDidReposition: function(model, resp, options) {
      this.triggerReposition(model);
    },

    canAcceptParent: function(parent) {
      return this.app.validateRelationship(parent, this.model);
    },

    startBeingDragged: function(event) {
      NodeViewBase.prototype.startBeingDragged.apply(this, arguments);

      // only on a left click.
      if ( event.which !== 1 )
        return;

      var placeholder = this.placeholder = $('<li class="drag_placeholder">&nbsp;</li>').css({
        width: this.$el.width(),
        padding: this.$el.css('padding')
      });

      this.$el.after(placeholder);
    },

    cssClasses: function() {
      return this.model.get('css_classes');
    }
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
      this.$el.css({
        'position': 'relative'
      });

      var $pointerEventsCatcher = $('<div class="pointer_event_catcher">')
        .css({
          'z-index': 51,
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
