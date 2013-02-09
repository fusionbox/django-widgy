define([ 'underscore', 'components/widget/component' ], function(_, widget) {

  var TableView = widget.View.extend({
    initialize: function() {
      widget.View.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'block',
        'unblock',
        'refresh'
      );

      this.listenTo(this.model.node.children, 'refreshTable', this.refresh)
          .listenTo(this.model.node.children, 'blockTable', this.block);
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

    refresh: function() {
      this.model.node.fetch({
        app: this.app,
        success: this.unblock,
        resort: true
      });
    }
  });

  return _.extend({}, widget, {
    View: TableView
  });
});
