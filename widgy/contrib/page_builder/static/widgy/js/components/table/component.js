define([ 'underscore', 'jquery', 'components/widget/component' ], function(_, $, widget) {

  var TableView = widget.View.extend({
    initialize: function() {
      widget.View.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'block',
        'unblock',
        'refresh'
      );
    },

    block: function() {
      if ( ! this.overlay )
        this.overlay = $('<div class="overlay"></div>').appendTo(this.el);
    },

    unblock: function() {
      if ( this.overlay ) {
        this.overlay.remove();
        delete this.overlay;
      }
    },

    refresh: function(options) {
      this.node.fetch(_.extend({
        app: this.app,
        success: this.unblock
      }, options));
    }
  });

  return _.extend({}, widget, {
    View: TableView
  });
});
