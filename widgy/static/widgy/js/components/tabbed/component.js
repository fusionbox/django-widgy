define([ 'underscore', 'widgy.backbone', 'components/widget/component' ], function(_, Backbone, widget) {

  var TabbedView = widget.View.extend({
    events: Backbone.extendEvents(widget.View, {
      'click .tabbed > .widget > .node_children .drag-row': 'showTab'
    }),

    showTab: function(event) {
      var view = this.list.findByEl($(event.target).parents('.node')[0]);

      this.$current.html(view.$preview);
      this.$current.append(view.$children);

      return false;
    },

    renderPromise: function() {
      return widget.View.prototype.renderPromise.apply(this, arguments).then(function(view) {
        view.$current = view.$('.current:last');
        return view;
      });
    }
  });

  return _.extend({}, widget, {
    View: TabbedView
  });
});
