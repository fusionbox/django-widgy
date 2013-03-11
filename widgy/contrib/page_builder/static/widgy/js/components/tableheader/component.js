define([ 'underscore', 'lib/q', 'components/widget/component' ], function(_, Q, widget) {

  var TableHeaderView = widget.View.extend({
    initialize: function() {
      widget.View.prototype.initialize.apply(this, arguments);

      this
        .listenTo(this.collection, 'destroy_child', this.parent.block)
        .listenTo(this.collection, 'destroy', this.parent.refresh)
        .listenTo(this.collection, 'receive_child', this.parent.block)
        .listenTo(this.collection, 'sort', this.moveColumn);
    },

    moveColumn: function(collection, options) {
      // Avoid recursion.
      if ( options && options.moveColumn )
        return;

      this.parent.refresh({moveColumn: true, resort: true});
    },

    addChild: function() {
      var parent = this,
          table = this.parent,
          promise = this.addChildPromise.apply(this, arguments);

      if ( promise ) {
        promise.then(function(node_view) {
          return Q(table.refresh({sort_silently: true})).then(function() {
            parent.resortChildren();
          });
        }).done();
      }

      return promise;
    }
  });

  return _.extend({}, widget, {
    View: TableHeaderView
  });
});
