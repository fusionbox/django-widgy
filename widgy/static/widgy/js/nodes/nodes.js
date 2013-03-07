define([ 'exports', 'jquery', 'underscore', 'widgy.backbone', 'lib/q', 'shelves/shelves', 'modal/modal',
    'text!./node.html',
    'text!./drop_target.html',
    'text!./popped_out.html',
    'nodes/base',
    'nodes/models'
    ], function(exports, $, _, Backbone, Q, shelves, modal,
      node_view_template,
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
    template: node_view_template,

    events: function() {
      return _.extend({}, DraggableView.prototype.events , {
        'click .delete': 'delete',
        'click .pop_out': 'popOut',
        'click .pop_in': 'closeSubwindow'
      });
    },

    initialize: function() {
      DraggableView.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'renderChildren',
        'addChild',
        'addDropTargets',
        'createDropTarget',
        'clearDropTargets',
        'startDrag',
        'stopDrag',
        'stopDragging',
        'dropChildView',
        'receiveChildView',
        'renderContent',
        'resortChildren',
        'popOut',
        'popIn',
        'closeSubwindow'
        );

      this.collection = this.model.children;
      this.drop_targets_list = new Backbone.ViewList();

      this
        .listenTo(this.collection, 'add', this.addChild)
        .listenTo(this.collection, 'reset', this.renderChildren)
        .listenTo(this.collection, 'sort', this.resortChildren);

      this
        .listenTo(this.model, 'remove', this.close);

      this.list = new Backbone.ViewList();
    },

    isRootNode: function() {
      return ! this.parent;
    },

    onClose: function() {
      DraggableView.prototype.onClose.apply(this, arguments);

      if ( this.content_view ) {
        this.content_view.close();
        delete this.content_view;
      }

      this.list.closeAll();
    },

    dontShowChildren: function() {
      return this.model.pop_out === 2 && ! this.isRootNode();
    },

    renderChildren: function() {
      debug.call(this, 'renderChildren');
      if ( this.dontShowChildren() )
        return;

      this.list.closeAll();
      var self = this;
      return Q.all(this.collection.map(this.addChild)).then(function() {
        self.resortChildren();
      });
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

      var self = this;

      return node_view.renderPromise().then(function(node_view) {
        self.$children.append(node_view);
      });
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
      debug.call(this, 'stopDrag', callback);

      if ( this.hasShelf() && this.dragged_view ) {
        callback(this.stopDragging());
      } else {
        // propagate event
        this.trigger('stopDrag', callback);
      }
    },

    getShelf: function() {
      if ( this.model.pop_out == 2 && ! this.isRootNode() )
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

      return this.app.validateRelationship(parent, this.model.content);
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
        parent_id: this.model.id,
        right_id: right ? right.id : null
      };

      this.collection.trigger('receive_child');
      dragged_view.model.save(attributes, {
        success: this.collection.reposition,
        error: modal.raiseError,
        app: this.app
      });
    },

    saveAt: function(attributes, options) {
      this.model.save(attributes, options);
    },

    hasShelf: function() {
      return this.model.shelf || this.isRootNode();
    },

    render: function() {
      debug.call(this, 'render');
      DraggableView.prototype.render.apply(this, arguments);

      this.$children = this.$el.find(' > .widget > .node_children');
      this.$content = this.$el.find(' > .widget > .content ');

      this.renderChildren();

      if ( this.hasShelf() ) {
        this.renderShelf();
      }

      this.model.ready(this.renderContent);

      return this;
    },

    renderPromise: function() {
      return DraggableView.prototype.renderPromise.apply(this, arguments).then(function(view) {
        view.$children = view.$(' > .widget > .node_children');
        view.$content = view.$(' > .widget > .content ');

        var promises = [];

        promises.push(view.renderChildren());

        if ( view.hasShelf() ) {
          promises.push(view.renderShelf());
        }

        promises.push(view.model.ready(view.renderContent));

        return Q.all(promises).thenResolve(view);
      });
    },

    /**
     * Because of how awesome Q is, renderContent and renderShelf
     * don't need to return promises, but they could.
     */
    renderContent: function() {
      if ( this.content_view )
        return;

      console.log(this.model.__class__, 'renderContent');

      this.content_view = new this.model.component.View({
        model: this.model.content,
        el: this.$content,
        app: this.app
      });

      this.content_view.renderPromise()
        .then(_.bind(function(content_view) {
          // when we are popped out, we need to remove our own pop out button.
          if ( this.isRootNode() ) {
            content_view.$('.pop_out').remove();
          }
        }, this))
        .done();
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

      var self = this;
      this.$children.before(shelf.render().el);
      // position sticky
      if ( this.isRootNode() ) {
        $(window).scroll(function() {
          var upper_bound = self.el.offsetTop,
              lower_bound = upper_bound + self.el.offsetHeight - shelf.el.offsetHeight,
              margin_top = Math.max(0, Math.min(window.scrollY - upper_bound, lower_bound - upper_bound) - 60);

          shelf.el.style.marginTop = margin_top + 'px';
        });
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
      $(window).on('unload.widgyPopOut-' + this.cid, this.popIn);

      this.collection.reset();
      this.content_view.close();
      delete this.content_view;
      this.$el.html(this.renderTemplate(popped_out_template, this.toJSON()));
    },

    popIn: function(event) {
      debug.call(this, 'popIn');

      event.preventDefault();
      event.stopPropagation();

      // we're popped in so don't popIn again when we leave this
      // page.
      $(window).off('.widgyPopOut-' + this.cid);

      this.model.fetch({
        app: this.app,
        resort: true,
        success: this.render
      });

      return false;
    },

    closeSubwindow: function() {
      if ( this.subwindow )
        this.subwindow.close();
      return false;
    },

    cssClasses: function() {
      return this.model.css_classes;
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


  return _.extend({}, models, {
    DropTargetView: DropTargetView,
    NodeView: NodeView
  });

});
