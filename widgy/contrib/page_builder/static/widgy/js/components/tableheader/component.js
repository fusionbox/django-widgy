define([ 'underscore', 'components/widget/component' ], function(_, widget) {

  var TableHeaderView = widget.View.extend({
    initialize: function() {
      widget.View.prototype.initialize.apply(this, arguments);

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

  var TableHeader = widget.Model.extend({
    viewClass: TableHeaderView
  });

  return _.extend({}, widget, {
    Model: TableHeader,
    View: TableHeaderView
  });
});
