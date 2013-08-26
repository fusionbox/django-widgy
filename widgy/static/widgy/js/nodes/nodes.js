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
        'deleteSelf',
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
        'prepareChild',
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

      this.list = new Backbone.ViewList();
    },

    isRootNode: function() {
      return ! this.parent;
    },

    onClose: function() {
      DraggableView.prototype.onClose.apply(this, arguments);

      this.list.closeAll();
      if ( this.hasShelf() )
        this.shelf.close();
    },

    dontShowChildren: function() {
      return this.content.get('pop_out') === 2 && ! this.isRootNode();
    },

    onMouseDown: function(event) {
      if ( $(event.target).is('.title, .drag-row, .drag_handle') && this.content.get('draggable') ) {
        return DraggableView.prototype.onMouseDown.apply(this, arguments);
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

    prepareChild: function(child_view) {
      this
        .listenTo(child_view, 'startDrag', this.startDrag)
        .listenTo(child_view, 'stopDrag', this.stopDrag);

      return child_view;
    },

    addChildPromise: function(node, collection, options) {
      var parent = this;

      options = (options || {});
      _.defaults(options, {
        sort_now: true
      });

      return node.ready(function(model) {
        return new model.component.View({
          model: node,
          parent: parent,
          app: parent.app
        });
      })
      .then(this.prepareChild)
      .then(function(node_view) {
        parent.app.node_view_list.push(node_view);
        if ( options && options.index ) {
          parent.list.push(node_view, {at: options.index});
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
      this.list.set(new_list);
    },

    'delete': function(event) {
      // TODO: A better UI experience would be undo, but this is a stop gap.
      this.$el.addClass('deleting');
      modal.confirm(
        'Are you sure you want to delete this ' + this.content.get('display_name') + '?',
        this.deleteSelf,
        _.bind(function() {
          this.$el.removeClass('deleting');
        }, this)
      );
      return false;
    },

    deleteSelf: function() {
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
    },

    startDrag: function(dragged_view) {
      if ( ( this.hasShelf() && ! dragged_view.model.id || this.isRootNode() )) {
        this.dragged_view = dragged_view;
        this.addDropTargets(dragged_view);
      } else {
        // propagate event
        this.trigger('startDrag', dragged_view);
      }
    },

    stopDragging: function() {
      var dragged_view = this.dragged_view;
      delete this.dragged_view;

      this.clearDropTargets();

      dragged_view.stopBeingDragged();

      return dragged_view;
    },

    stopDrag: function(callback) {
      if ( this.hasShelf() && this.dragged_view ) {
        var dragged_view = this.stopDragging();
        if ( callback )
          callback(dragged_view);
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

      if (this.canAcceptChild(view)) {
        $children.prepend(this.createDropTarget(view).el);
        this.list.each(function(node_view) {
          var drop_target = that.createDropTarget(view).$el.insertAfter(node_view.el);
        }, this);
      }
    },

    createDropTarget: function(view) {
      var drop_target = new DropTargetView();
      drop_target.on('dropped', this.dropChildView);
      this.drop_targets_list.push(drop_target);

      if ( this.list.contains(view) ) {
        var view_index = this.list.indexOf(view),
            target_index = this.drop_targets_list.size() - 1;
        if ( view_index == target_index ) {
          drop_target.activate().$el
            .addClass('previous')
            .attr('style', function(i, s) { return (s||'') + ' height: '+ view.$el.height() +'px !important;'; });
          if ( view_index == this.list.size() - 1 )
            drop_target.$el.addClass('nm');
        } else if ( view_index == target_index - 1 ) {
          drop_target.$el.hide();
        }
      }

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
      this.cleanUp();
      this.renderPromise().done();
    },

    cleanUp: function() {
      this.$children.remove();
      this.$preview.remove();
      if (this.shelf)
        this.shelf.close();
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

          view.trigger('rendered', view);

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
      console.log('renderShelf');

      var shelf = this.shelf = this.makeShelf();

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

      return shelf;
    },

    makeShelf: function() {
      return new shelves.ShelfView({
        collection: new shelves.ShelfCollection({
            node: this.node
          }),
        app: this.app
      });
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
          'padding': '20px 40px',
          'position': 'absolute',
          'top': '-20px',
          'left': '-40px'
        });
      this.$el.prepend($pointerEventsCatcher);

      return this;
    },

    activate: function(event) {
      this.$el.addClass('active');
      return this;
    },

    deactivate: function(event) {
      this.$el.removeClass('active')
              .css('height', '');
      return this;
    }
  });


  return _.extend({}, models, {
    DropTargetView: DropTargetView,
    NodeView: NodeView
  });

});
