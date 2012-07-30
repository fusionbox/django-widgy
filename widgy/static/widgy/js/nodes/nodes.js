define([ 'jquery', 'widgy.backbone', 'widgy.contents',
    'text!nodes/node_view.html',
    'text!nodes/drop_target_view.html',
    ], function($, Backbone, contents,
      node_view_template,
      drop_target_view_template
      ) {

  /**
   * Nodes provide structure in the tree.  Nodes only hold data that deals with
   * structure.  Any other data lives in it's content.
   *
   * A node will have two properties: `children` and `content`.  `children` is
   * a NodeCollection which is basically just a list of child nodes. `content`
   * is model containing all non-structure information about a node.  The
   * actual Model Class that defines the content property depends on the
   * content type.  See `widgy.contents.js` for more information.
   */
  var Node = Backbone.Model.extend({
    urlRoot: '/admin/widgy/node/',

    initialize: function() {
      Backbone.Model.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'instantiateContent'
        );
      // content gets set because it is in the JSON for the node.  We need to
      // unset it as it is not an attribute, but a property.  We also need to
      // instantiate it as a real Content Model.
      this._content = this.get('content');
      this.unset('content');

      // This is asynchronous because of requirejs.
      contents.getModel(this._content.__module_name__, this.instantiateContent);

      // same as content.  We need to actually instantiate the NodeCollection
      // and set it as a property, not an attribute.
      var children = this.get('children');
      this.children = new NodeCollection(children);
      this.unset('children');
    },

    instantiateContent: function(model_class) {
      this.content = new model_class(this._content);
      delete this._content;

      this.trigger('loaded:content', this.content);
    }
  });


  /**
   * NodeCollections provide the children interface for nodes and also an
   * interface to NodeViews for how to handle child NodeViews.
   */
  var NodeCollection = Backbone.Collection.extend({
    model: Node,
  });


  /**
   * The NodeView provides an interface to the node.  It will also create a
   * ContentView for the node's content.  Additionally, it will create child
   * NodeViews for all of the nodes in children.
   *
   * Properties:
   *
   * -  `this.model` is the node.
   * -  `this.collection` is the node's children (Also available in
   *    `this.model.children`.
   * -  `this.app` is the instance of AppView
   */
  var NodeView = Backbone.View.extend({
    className: 'node',
    template: node_view_template,
    
    events: {
      'mousedown .drag_handle': 'startDrag'
    },

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'addAll',
        'addOne',
        'startDrag',
        'followMouse',
        'stopDrag',
        'reposition',
        'addDropTargets',
        'createDropTarget',
        'dropChildView',
        'clearDropTargets'
      );

      this.collection
        .on('reset', this.addAll)
        .on('add', this.addOne);

      this.model
        .on('remove', this.close)
        .on('change', this.reposition);

      this.app = options.app;
      this.app.node_view_list.push(this);

      this.model.bind('loaded:content', this.render);

      this.drop_targets_list = new Backbone.ViewList;
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(node) {
      var node_view = new NodeView({
        model: node,
        collection: node.children,
        app: this.app
      });

      this.$children.append(node_view.el);
    },

    /**
     * `startDrag`, `stopDrag`, `followMouse`, and `reposition` all deal with a
     * NodeView itself being dragged around.
     */
    startDrag: function(event) {
      event.preventDefault();
      event.stopPropagation();

      this.app.startDrag(this);

      // hide drop target behind me.
      this.$el.prev().hide();
      this.clearDropTargets();

      // follow mouse real quick, don't wait for mousemove.
      this.followMouse(event);

      this.$el.addClass('being_dragged');
    },

    stopDrag: function() {
      this.$el.css({
        position: 'static'
      });

      this.$el.removeClass('being_dragged');
    },

    followMouse: function(event) {
      this.$el.css({
        position: 'absolute',
        top: event.pageY,
        left: event.pageX
      });
    },

    /**
     * This method puts the NodeView in the correct spot after a model change.
     */
    reposition: function(model, options) {
      if ( model.get('left_id') ) {
        if ( model.get('left_id') === model.id )
          return;

        var left_view = this.app.node_view_list.findById(model.get('left_id'));
        left_view.$el.after(this.el);
      } else {
        var parent_view = this.app.node_view_list.findById(model.get('parent_id'));
        parent_view.$children.prepend(this.el);
      }
      // TODO: fix collections and stuff.
    },

    /**
     * `addDropTargets`, `createDropTarget`, `dropChildView`, and
     * `clearDropTargets` all deal with a different NodeView being dragged.  It
     * is confusing that these methods are on the same class that the methods
     * dealing with being dragged around are on, but that's the nature of the
     * beast with recursive nodes.
     */
    createDropTarget: function() {
      var drop_target = new DropTargetView;
      drop_target.on('dropped', this.dropChildView);
      this.drop_targets_list.push(drop_target);

      return drop_target.render();
    },

    addDropTargets: function() {
      var $children = this.$children,
          that = this;

      $children.prepend(this.createDropTarget().el);
      $children.children('.node').each(function(index, elem) {
        $(elem).after(that.createDropTarget().el);
      });
    },

    /**
     * This is the method that is called when the NodeView that is being
     * dragged is dropped on one of my drop targets.
     */
    dropChildView: function(view) {
      var $children = this.$children;
      var index = view.$el.index() / 2;

      // We need to stop the drag before finding the left node.
      // `this.app.stopDrag` will clear all of the drop targets, so we need to
      // remove them before we can get elements by index.
      var dragged_view = this.app.stopDrag();

      var left_id = null;

      // If index is 0 there is no left element and we want to set
      // it to null.
      if ( index !== 0 ) {
        var left_el = $children.children().eq(index - 1)[0],
            left_view = this.app.node_view_list.findByEl(left_el);

        left_id = left_view.model.id;
      }

      // pessimistic save (for now).
      dragged_view.model.save({
        parent_id: this.model.id,
        left_id: left_id
      }, {wait: true});
    },

    clearDropTargets: function() {
      this.drop_targets_list.closeAll();
    },

    render: function(content) {
      Backbone.View.prototype.render.apply(this, arguments);

      var view_class = content.getViewClass();

      this.content_view = new view_class({
        model: content
      });

      this.$content = this.$('.content:first');
      this.$content.append(this.content_view.render().el);

      this.$children = this.$('.children:first');

      // TODO: investigate possible problems with this.
      this.addAll();

      return this;
    }
  });


  var DropTargetView = Backbone.View.extend({
    className: 'node_drop_target',

    template: drop_target_view_template,

    triggers: {
      'mouseup': 'dropped'
    }
  });


  return {
    Node: Node,
    NodeCollection: NodeCollection,
    NodeView: NodeView,
    DropTargetView: DropTargetView
  };

});
