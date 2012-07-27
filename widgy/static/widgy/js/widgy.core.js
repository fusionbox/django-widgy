;(function() {
  var exports = window.Widgy = {
    nodes: {},
    contents: {},
    editors: {}
  };


  /**
   * Our base Backbone classes.
   */
  var View = exports.View = Backbone.View.extend({
    /**
     * Adds a method for killing zombies.
     *
     * Based on Derick Bailey's blog post:
     * http://lostechies.com/derickbailey/2011/09/15/zombies-run-managing-page-transitions-in-backbone-apps/
     */
    close: function() {
      this.remove();
      this.unbind();
      this.onClose();
    },

    onClose: function() {},

    template: false,

    render: function() {
      if (this.template) {
        this.$el.html(ich[this.template](this.model.toJSON()));
      }

      return this;
    }
  });


  /**
   * Widgy Contents
   */

  // Helper method to create a ContentModel, that finds the correct model based
  // on the node content.
  var createContent = exports.contents.createContent = function(node) {
    var content = node.content,
        children = content.children;

    content.children = new ContentCollection;
    content.node_id = node.id;
    var model = new exports.contents[content.object_name](content);

    model._children = children;

    return model;
  };


  var ContentModel = exports.contents.ContentModel = Backbone.Model.extend({
    urlRoot: '/admin/widgy/',

    initialize: function() {
      // debugging
      this.type = this.get('model');
    },

    url: function() {
      var url = this.urlRoot + this.get('model') + '/';

      if ( ! this.isNew() ) {
        url = url + this.id + '/';
      }

      return url;
    }
  });


  var ContentCollection = exports.contents.ContentCollection = Backbone.Collection.extend({
    _prepareModel: function(node, options) {
      options || (options = {});
      var model = createContent(node);
      return model;
    }
  });


  /**
   * Widgy Nodes
   */
  var createNode = exports.nodes.createNode = function(model) {
    return new exports.nodes[model.viewClass]({
      model: model,
      collection: model.get('children')
    });
  };

  var node_map = exports.nodes.node_map = {};

  var NodeView = exports.nodes.NodeView = View.extend({
    className: 'node',

    initialize: function() {
      this.children_views = [];

      _.bindAll(this, 'addAll', 'addOne');
      this.collection.on('reset', this.addAll);
      this.collection.on('add', this.addOne);
    },

    addAll: function() {
      this.collection.each(this.addOne);
    },

    addOne: function(model) {
      var node = createNode(model);

      this.children_views.push(node);
      this.$el.append(node.render().el);

      node.collection.reset(model._children);

      node_map[model.get('node_id')] = this.collection;
    }
  });


  var WidgetView = exports.nodes.WidgetView = NodeView.extend({
    events: {
      'click .edit': 'editWidget',
      'change .right_of': 'moveToRightOf'
    },

    initialize: function() {
      NodeView.prototype.initialize.apply(this, arguments);
      this.model.on('change', this.render, this);
    },

    editWidget: function(event) {
      event.preventDefault();

      var edit_view = createEditor(this);
      this.$el.append(edit_view.render().el);
    },

    moveToRightOf: function(event) {
      var id = +this.$('.right_of').val();
          collection = node_map[id],
          left = collection.where({node_id: id})[0];

      console.log(arguments, left);
    }
  });


  /**
   * Widgy Editors
   */
  var createEditor = exports.editors.createEditor = function(view) {
    return new exports.editors[view.editorClass]({model: view.model});
  };
  
  
  var EditorView = exports.editors.EditorView = View.extend({
    events: {
      'submit form': 'handleForm',
      'click .cancel': 'close'
    },

    handleForm: function(event) {
      event.preventDefault();
      var values = this.hydrateForm();

      this.model.save(values);
      this.close();
    },

    hydrateForm: function() {
      return this.$('form').serializeObject();
    }
  });


  /**
   * Helpers
   */
  Widgy.noop = function(){};


  /**
   * jQuery Plugins
   */
  jQuery.fn.serializeObject = function()
  {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
      if (o[this.name] !== undefined) {
        if (!o[this.name].push) {
          o[this.name] = [o[this.name]];
        }
        o[this.name].push(this.value || '');
      } else {
        o[this.name] = this.value || '';
      }
    });
    return o;
  };
})();
