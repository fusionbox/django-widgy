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

    render: function() {
      this.$el.html(ich[this.template](this.model.toJSON()));

      return this;
    }
  });


  /**
   * Widgy Contents
   */
  var createContent = exports.contents.createContent = function(content) {
    return new exports.contents[content.object_name](content);
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


  /**
   * Widgy Nodes
   */
  var createNode = exports.nodes.createNode = function(model) {
    return new exports.nodes[model.viewClass]({model: model});
  };

  var NodeView = exports.nodes.NodeView = View.extend({
    initialize: function() {
      this.children = [];
      _.each(this.model.get('children'), this.instantiateChild, this);
    },

    instantiateChild: function(child) {
      this.children.push(createNode(createContent(child.content)));
    },

    widgyRender: function() {
      this.render();

      _.each(this.children, this.appendChild, this);

      return this;
    },

    appendChild: function(child) {
      this.$el.append(child.widgyRender().el);
    }
  });


  var WidgetView = exports.nodes.WidgetView = NodeView.extend({
    events: {
      'click .edit': 'editWidget'
    },

    initialize: function() {
      this.model.on('change', this.render, this);
    },

    editWidget: function(event) {
      event.preventDefault();

      var edit_view = createEditor(this);
      this.$el.append(edit_view.render().el);
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
