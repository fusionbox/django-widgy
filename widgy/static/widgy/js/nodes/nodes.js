define([ 'exports', 'jquery', 'underscore', 'widgy.backbone', 'lib/q', 'shelves/shelves', 'modal/modal',
    'text!./drop_target.html',
    'text!./popped_out.html',
    'nodes/base',
    'nodes/models'
    ], function(exports, $, _, Backbone, Q, shelves, modal,
      drop_target_view_template,
      popped_out_template,
      DraggableView,
      models
      ) {

  var debug = function(where) {
    console.log(where, this, _.rest(arguments));
  };


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
  var NodeView = DraggableView.extend({
    events: Backbone.extendEvents(DraggableView, {
      'click .delete': 'delete',
      'click .pop_out': 'popOut',
      'click .pop_in': 'closeSubwindow'
    }),

    initialize: function() {
      DraggableView.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'renderChildren',
        'addChild',
        'addChildPromise',
        'addDropTargets',
        'createDropTarget',
        'clearDropTargets',
        'startDrag',
        'stopDrag',
        'stopDragging',
        'dropChildView',
        'receiveChildView',
        'resortChildren',
        'getRenderPromises',
        'rerender',
        'popOut',
        'popIn',
        'closeSubwindow'
        );

      this.node = this.model;
      this.content = this.node.content;
      this.collection = this.node.children;
      this.drop_targets_list = new Backbone.ViewList();

      this
        .listenTo(this.collection, 'add', this.addChild)
        .listenTo(this.collection, 'reset', this.renderChildren)
        .listenTo(this.collection, 'sort', this.resortChildren);

      this
        .listenTo(this.node, 'remove', this.close);

      this
        .listenTo(this.content, 'change:preview_template', this.rerender);

      this.list = new Backbone.ViewList();
    },

    isRootNode: function() {
      return ! this.parent;
    },

    onClose: function() {
      DraggableView.prototype.onClose.apply(this, arguments);

      this.list.closeAll();
    },

    dontShowChildren: function() {
      return this.content.get('pop_out') === 2 && ! this.isRootNode();
    },

    startBeingDragged: function(event) {
      if ( $(event.target).is('.title, .drag-row, .drag_handle') && this.content.get('draggable') ) {
        return DraggableView.prototype.startBeingDragged.apply(this, arguments);
      } else {
        return false;
      }
    },

    renderChildren: function() {
      if ( this.dontShowChildren() )
        return;

      this.list.closeAll();
      var self = this;
      return Q.all(this.collection.map(this.addChildPromise)).then(function() {
        self.resortChildren();
      });
    },

    addChildPromise: function(node, collection, options) {
      var parent = this;

      options = (options || {});
      _.defaults(options, {
        sort_now: true
      });

      return node.ready(function(model) {
        var node_view = new model.component.View({
          model: node,
          parent: parent,
          app: parent.app
        });

        parent
          .listenTo(node_view, 'startDrag', parent.startDrag)
          .listenTo(node_view, 'stopDrag', parent.stopDrag);

        parent.app.node_view_list.push(node_view);
        if ( options && options.index ) {
          parent.list.list.splice(options.index, 0, node_view);
        } else {
          parent.list.push(node_view);
        }

        return node_view.renderPromise().then(function(node_view) {
          parent.$children.append(node_view);

          return node_view;
        });
      });
    },

    addChild: function() {
      if ( this.dontShowChildren() )
        return;

      var parent = this,
          promise = this.addChildPromise.apply(this, arguments);

      if ( promise ) {
        promise.then(function(node_view) {
          parent.resortChildren();
        }).done();
      }

      return promise;
    },

    resortChildren: function() {
      var new_list = [];
      this.collection.each(function(model) {
        var node_view = this.list.findByModel(model);
        if ( node_view ) {
          this.$children.append(node_view.el);
          new_list.push(node_view);
        }
      }, this);
      this.list.list = new_list;
    },

    'delete': function(event) {
      var spinner = new Backbone.Spinner({el: this.$('.delete:first')}),
          model = this.node;

      var error = function() {
        spinner.restore();
        modal.ajaxError.apply(this, arguments);
      };

      this.node.collection.trigger('destroy_child');
      this.node.destroy({
        wait: true,
        error: error,
        app: this.app
      });
      return false;
    },

    startDrag: function(dragged_view) {
      if ( ( this.hasShelf() && ! dragged_view.model.id || this.isRootNode() )) {
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
      if ( this.hasShelf() && this.dragged_view ) {
        callback(this.stopDragging());
      } else {
        // propagate event
        this.trigger('stopDrag', callback);
      }
    },

    getShelf: function() {
      if ( this.content.get('pop_out') == 2 && ! this.isRootNode() )
        return null;
      else if ( this.hasShelf() )
        return this.shelf;
      else
        return this.parent.getShelf();
    },

    // TODO: move these methods to model.
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

      return this.app.validateRelationship(parent, this.content);
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

      var node = dragged_view.model;

      // It's already mine and it was dragged into its own drop target.
      if ( index === this.collection.indexOf(dragged_view) )
        return;

      // This will return the model that we want at our right or undefined.
      var right = this.collection.at(index);

      // Bail if it didn't move.
      if ( this.model === node.getParent() && right === node )
        return;

      var attributes = {
        parent_id: this.node.id,
        right_id: right ? right.id : null
      };

      this.collection.trigger('receive_child');
      dragged_view.model.save(attributes, {
        success: this.collection.reposition,
        error: modal.ajaxError,
        app: this.app
      });
    },

    hasShelf: function() {
      return this.content.get('shelf') || this.isRootNode();
    },

    getTemplate: function() {
      return this.content.get('preview_template');
    },

    rerender: function() {
      this.renderPromise().done();
    },

    renderNode: function() {
      return DraggableView.prototype.renderPromise.apply(this, arguments).then(function(view) {
        view.$children = view.$(' > .widget > .node_children');
        view.$preview = view.$(' > .widget > .preview ');

        if ( view.isRootNode() && view.content.get('pop_out') ) {
          view.$('.pop_out:first').remove();
        }

        return view;
      });
    },

    renderPromise: function() {
      return this.renderNode().then(function(view) {
        return Q.all(view.getRenderPromises()).then(function() {
          if ( view.app.compatibility_data )
            view.app.updateCompatibility(view.app.compatibility_data);

          return view;
        });
      });
    },

    render: function() {
      throw new Error("You may not use NodeView.render, please use NodeView.renderPromise.");
    },

    getRenderPromises: function() {
      var promises = [
        this.renderChildren()
        ];

      if ( this.hasShelf() ) {
        promises.push(this.renderShelf());
      }

      return promises;
    },

    renderShelf: function() {
      if (this.shelf)
        this.shelf.remove();

      var shelf = this.shelf = new shelves.ShelfView({
        collection: new shelves.ShelfCollection({
            node: this.node
          }),
        app: this.app
      });

      this.listenTo(shelf, 'startDrag', this.startDrag)
          .listenTo(shelf, 'stopDrag', this.stopDrag);

      var self = this;
      this.$children.before(shelf.render().el);
      // position sticky
      if ( this.isRootNode() ) {
        var mezzanine_fixed_toolbar_height = 60,
            // TODO: figure out what is at the root of this.
            fix_overscrolling_pixels = 4;

        $(window).scroll(function() {
          // upper_bound is the highest the top of the shelf can be
          // lower_bound is the lower the top of the shelf can be
          var upper_bound = self.el.offsetTop,
              lower_bound = upper_bound + self.el.offsetHeight - shelf.el.offsetHeight,
              margin_top = Math.max(0, Math.min(window.scrollY, lower_bound) - upper_bound - mezzanine_fixed_toolbar_height - fix_overscrolling_pixels);

          shelf.el.style.marginTop = margin_top + 'px';
        });
      }
    },

    toJSON: function() {
      var json = this.node.toJSON();
      if ( this.content )
        json.content = this.content.toJSON();

      return json;
    },

    popOut: function(event) {
      event.preventDefault();
      event.stopPropagation(); // our parent nodes

      this.subwindow = window.open(event.target.href, '', 'height=500,width=800,resizable=yes,scrollbars=yes');
      this.subwindow.widgyCloseCallback = this.popIn;

      // If they leave this page, pop back in.
      $(window).on('unload.widgyPopOut-' + this.cid, this.popIn);

      this.$el.addClass('poppedOut');
      this.$preview.html(this.renderTemplate(popped_out_template, this.toJSON()));
    },

    popIn: function(event) {
      event.preventDefault();
      event.stopPropagation();

      // we're popped in so don't popIn again when we leave this
      // page.
      $(window).off('.widgyPopOut-' + this.cid);

      this.$el.removeClass('poppedOut');

      this.node.fetch({
        app: this.app,
        resort: true,
        success: this.rerender
      });

      return false;
    },

    closeSubwindow: function() {
      if ( this.subwindow )
        this.subwindow.close();
      return false;
    },

    cssClasses: function() {
      return this.content.get('css_classes');
    }
  });


  var DropTargetView = Backbone.View.extend({
    tagName: 'li',
    className: 'node_drop_target',
    template: drop_target_view_template,

    triggers: {
      'mouseup': 'dropped'
    },

    events: Backbone.extendEvents(Backbone.View, {
      'mouseenter': 'activate',
      'mouseleave': 'deactivate'
    }),

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


  return _.extend({}, models, {
    DropTargetView: DropTargetView,
    NodeView: NodeView
  });

});
