define([ 'widgy.contents', 'widgets/widgets' ], function(contents, widgets) {

  var TableView = widgets.WidgetView.extend({
    initialize: function() {
      widgets.WidgetView.prototype.initialize.apply(this, arguments);

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
        success: this.unblock
      });
    }
  });

  var Table = contents.Content.extend({
    viewClass: TableView
  });

  return Table;
});
