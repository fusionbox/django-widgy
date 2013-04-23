define([ 'underscore', 'widgy.backbone', 'components/widget/component' ], function(_, Backbone, widget) {

  var TabbedView = widget.View.extend({
    events: Backbone.extendEvents(widget.View, {
      'click .tabbed > .widget > .node_children .drag-row': 'showTabClick'
    }),

    showTabClick: function(event) {
      var view = this.list.findByEl($(event.target).parents('.node')[0]);
      this.showTab(view);

      return false;
    },

    showTab: function(view) {
      this.$children.find('.active').removeClass('active');
      view.$el.addClass('active');

      // previously, I was emptying the $current div and inserting the
      // elements; however, when you remove an element out of DOM it appears to
      // lose its events.  I'm doing it this way in order to not lose the
      // events.
      this.$current.children().hide();
      view.$preview.show();
      view.$children.show();

      if ( view.hasShelf() ) {
        view.shelf.$el.show();
      }

      return false;
    },

    renderNode: function() {
      return widget.View.prototype.renderNode.apply(this, arguments).then(function(view) {
        view.$current = view.$('.current:last');

        return view;
      });
    },

    renderPromise: function() {
      return widget.View.prototype.renderPromise.apply(this, arguments).then(function(view) {
        // Show the first tab on first render.
        // Does this always work?
        view.showTab(view.list.list[0]);

        return view;
      });
    },

    addChildPromise: function() {
      var parent = this;
      return widget.View.prototype.addChildPromise.apply(this, arguments).then(function(child_view) {
        if ( child_view.hasShelf() ) {
          console.log('addChildPromise');
          child_view.shelf.$el.hide().appendTo(parent.$current);
        }
        child_view.$preview.hide().appendTo(parent.$current);
        child_view.$children.hide().appendTo(parent.$current);

        return child_view;
      });
    }
  });

  return _.extend({}, widget, {
    View: TabbedView
  });
});
