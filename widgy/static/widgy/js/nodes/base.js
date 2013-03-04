define(['jquery', 'underscore', 'widgy.backbone'], function(
      $, _, Backbone
      ) {

  var bump = _.throttle(function(amount) {
    document.body.scrollTop += amount;
  }, 100);


  /**
   * Provides an interface for a draggable NodeView.  See NodeView for more
   * specific Node functionality related definition.  DraggablewView is exposed
   * for subclassing by a NodePreviewView and NodeView.
   */
  var DraggablewView = Backbone.View.extend({
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
        'canAcceptParent'
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

      clearInterval(this.bumpInterval);
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
    }
  });


  return DraggablewView;
});
