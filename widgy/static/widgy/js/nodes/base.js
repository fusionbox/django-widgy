define(['jquery', 'underscore', 'widgy.backbone', 'geometry'], function(
      $, _, Backbone, geometry
      ) {

  var bump = _.throttle(function(amount) {
    window.scrollBy(0, amount);
  }, 100);

  var BACKTICK = 96;


  /**
   * Provides an interface for a draggable NodeView.  See NodeView for more
   * specific Node functionality related definition.  DraggablewView is exposed
   * for subclassing by a NodePreviewView and NodeView.
   */
  var DraggablewView = Backbone.View.extend({
    tagName: 'li',
    className: 'node',
    distanceTrigger: 5,

    events: Backbone.extendEvents(Backbone.View, {
      'mousedown .drag-row': 'onMouseDown'
    }),

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'startBeingDragged',
        'followMouse',
        'stopBeingDragged',
        'canAcceptParent',
        'bindDragEvents',
        'unbindDocument',
        'checkDistance',
        'debugMode',
        'activateCollidingDropTargets'
      );

      this
        .listenTo(this.model, 'destroy', this.close)
        .listenTo(this.model, 'remove', this.close);

      this.app = options.app;
      this.parent = options.parent;
    },

    render: function() {
      Backbone.View.prototype.render.apply(this, arguments);
      _.each(this.cssClasses(), this.$el.addClass, this.$el);

      return this;
    },

    renderPromise: function() {
      return Backbone.View.prototype.renderPromise.apply(this, arguments)
        .then(function(self) {
          _.each(self.cssClasses(), self.$el.addClass, self.$el);
          return self;
        });
    },

    onMouseDown: function(event) {
      event.preventDefault();
      event.stopPropagation();

      // only on a left click.
      if ( event.which !== 1 || ! this.app.ready() )
        return false;

      // this is for checkDistance
      this.originalX = event.clientX;
      this.originalY = event.clientY;

      // Store the mouse offset in this container for followMouse to use.  We
      // need to get this before `this.app.startDrag`, otherwise the drop
      // targets screw everything up.
      var offset = this.$el.offset();
      this.cursorOffsetX = event.clientX - offset.left + (event.pageX - event.clientX);
      this.cursorOffsetY = event.clientY - offset.top + (event.pageY - event.clientY);

      $(document)
        .on('mouseup.' + this.cid, this.unbindDocument)
        .on('mousemove.' + this.cid, this.checkDistance);

      $(window).on('scroll.' + this.cid, _.bind(function() {
        // pass in a fake mouse event.
        this.startBeingDragged({
          clientY: this.originalY,
          clientX: this.originalX
        });
      }, this));

      return true;
    },

    unbindDocument: function(event) {
      $(document).off('.' + this.cid);
      $(window).off('.' + this.cid);
    },

    checkDistance: function(event) {
      var distance = Math.sqrt(Math.pow(event.clientY - this.originalY, 2) + Math.pow(event.clientX - this.originalX, 2));

      if ( distance > this.distanceTrigger ) {
        this.startBeingDragged(event);
      }
    },

    startBeingDragged: function(event) {
      this.unbindDocument();

      // follow mouse really quick, just in case they haven't moved their
      // mouse yet.
      this.followMouse(event);

      this.$el.css({
        width: this.$el.width(),
        'z-index': 50
      });
      this.$el.addClass('being_dragged');

      this.bindDragEvents();
      this.trigger('startDrag', this);
    },

    bindDragEvents: function() {
      var view = this;

      $(document)
        .on('mouseup.' + this.cid, this.stopBeingDragged)
        .on('mousemove.' + this.cid, this.followMouse)
        .on('selectstart.' + this.cid, function(){ return false; })
        // debugging helper
        .one('keypress.' + this.cid, function(event) {
          if ( event.which === BACKTICK )
            view.debugMode();
        });
    },

    debugMode: function(event) {
      var view = this;
      view.unbindDocument();

      $(document)
        // resume dragging
        .one('keypress.' + this.cid, function(event) {
          if ( event.which === BACKTICK )
            view.bindDragEvents();
        });
    },

    stopBeingDragged: function() {
      this.$el.css({
        top: '',
        left: '',
        width: '',
        'z-index': ''
      });

      this.unbindDocument();
      this.$el.removeClass('being_dragged');
      clearInterval(this.bumpInterval);

      this.app.visible_drop_targets.each(function(drop_target) {
        if ( drop_target.active )
          drop_target.trigger('dropped', drop_target);
      });

      this.trigger('stopDrag');
    },

    bumpAmount: function(clientY) {
      var direction,
          distance;

      if ( clientY < 100 ) {
        direction = -1;
        distance = clientY;
      } else {
        direction = 1;
        distance = Math.min(window.innerHeight - clientY, 100);
      }

      return direction * Math.pow((100 - distance) / 10, 2);
    },

    followMouse: function(mouse) {
      this.$el.css({
        top: (mouse.clientY - this.cursorOffsetY),
        left: (mouse.clientX - this.cursorOffsetX)
      });

      clearInterval(this.bumpInterval);

      var amount = this.bumpAmount(mouse.clientY);
      if ( amount ) {
        bump(amount);

        this.bumpInterval = setInterval(function() {
          bump(amount);
        }, 15);
      }

      this.activateCollidingDropTargets(mouse);
    },

    activateCollidingDropTargets: _.throttle(function(mouse) {
      var overlapping = this.app.visible_drop_targets.filterByOverlappingEl(this.el);
      var the_closest = _.min(overlapping, function(view) {
        return geometry.calculateDistance(view.el.getBoundingClientRect(), mouse.clientX, mouse.clientY);
      });
      this.app.visible_drop_targets.each(function(view) {
        if ( view !== the_closest )
          view.deactivate();
        else
          view.activate();
      });
    }, 50)
  });


  return DraggablewView;
});
