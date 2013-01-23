define([ 'widgy.contents', 'widgets/widgets' ], function(contents, widgets) {

  var TableHeaderView = widgets.WidgetView.extend({
    initialize: function() {
      widgets.WidgetView.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'refreshTable',
        'blockTable'
      );

      this.listenTo(this.model.node.children, 'position_child', this.refreshTable)
          .listenTo(this.model.node.children, 'destroy', this.refreshTable)
          .listenTo(this.model.node.children, 'receive_child', this.blockTable)
          .listenTo(this.model.node.children, 'destroy_child', this.blockTable);
    },

    refreshTable: function() {
      this.model.node.trigger('refreshTable');
    },

    blockTable: function() {
      this.model.node.trigger('blockTable');
    }
  });

  var TableHeader = contents.Content.extend({
    viewClass: TableHeaderView
  });

  return TableHeader;
});
