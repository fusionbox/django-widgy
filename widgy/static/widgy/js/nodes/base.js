define(['underscore', 'widgy.backbone'], function(
      _, Backbone
      ) {


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
        'canAcceptParent'
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

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);
      _.each(this.model.css_classes, this.$el.addClass, this.$el);

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


  return NodeViewBase;
});
