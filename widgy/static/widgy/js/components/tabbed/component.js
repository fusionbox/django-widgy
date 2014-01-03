define([ 'jquery', 'underscore', 'widgy.backbone', 'components/widget/component' ], function($, _, Backbone, widget) {

  var TabbedView = widget.View.extend({
    events: Backbone.extendEvents(widget.View, {
      'click .tabbed > .widget > .node_children .drag-row': 'showTabClick'
    }),

    initialize: function() {
      widget.View.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'stealThingsFromChild'
      );

      this.listenTo(this.collection, 'remove', this.showTabAfterTabDestroy);
    },

    showTabAfterTabDestroy: function(model, collection, options) {
      if(this.list.size() < 1) {
        return;
      }

      var index_to_show = options.index;

      if(index_to_show > 0) {
        index_to_show--;
      }

      this.showTab(this.list.at(index_to_show));
    },

    showTabClick: function(event) {
      if ( $(event.target).is('.preview') )
        return;

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
    },

    renderNode: function() {
      return widget.View.prototype.renderNode.apply(this, arguments).then(function(view) {
        view.$current = view.$('.current:last');

        return view;
      });
    },

    renderChildren: function() {
      var parent = this;
      return widget.View.prototype.renderChildren.apply(this, arguments).then(function() {
        // Show the first tab on first render.
        // Does this always work?
        if ( parent.list.size() )
          parent.showTab(parent.list.at(0));

        return parent;
      });
    },

    stealThingsFromChild: function(child_view) {
      if ( child_view.hasShelf() ) {
        child_view.shelf.$el.hide().appendTo(this.$current);
      }
      child_view.$preview.hide().appendTo(this.$current);
      child_view.$children.hide().appendTo(this.$current);

      this.showTab(child_view);

      return child_view;
    },

    prepareChild: function(child_view) {
      widget.View.prototype.prepareChild.apply(this, arguments);
      this.listenTo(child_view, 'rendered', this.stealThingsFromChild);
      return child_view;
    },

    createDropTarget: function(view) {
      var drop_target = widget.View.prototype.createDropTarget.apply(this, arguments);
      drop_target.$el.css('height', '');
      return drop_target;
    }
  });

  return _.extend({}, widget, {
    View: TabbedView
  });
});
