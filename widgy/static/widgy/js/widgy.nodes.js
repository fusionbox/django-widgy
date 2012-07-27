  var contents = {},
      nodes = {},
      editors = {};

  var createContent = function(content) {
    return new contents[content.model](content);
  };

  var createNode = function(model) {
    return new nodes[model.viewClass]({model: model});
  };

  var createEditor = function(view) {
    return new editors[view.editorClass]({model: view.model});
  };

  var ContentModel = Backbone.Model.extend({
    initialize: function() {
      this.type = this.get('model');
    },

    save: function(attrs, options) {
      this.set(attrs, options);
      console.log('"saved" model', attrs, options);
    }
  });

  contents.TwoColumnLayout = ContentModel.extend({
    viewClass: 'LayoutView'
  });

  contents.Bucket = ContentModel.extend({
    viewClass: 'BucketView'
  });

  contents.TextContent = ContentModel.extend({
    viewClass: 'TextContentView'
  });


  var NodeView = Widgy.View.extend({
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


  nodes.LayoutView = NodeView.extend({
    render: function() {}
  }); 

  nodes.BucketView = NodeView.extend({
    tagName: 'section',
    className: 'bucket',

    template: 'bucket'
  });

  var WidgetView = NodeView.extend({
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

  nodes.TextContentView = WidgetView.extend({
    template: 'text_content',
    editorClass: 'TextContentEditView'
  });

  editors.TextContentEditView = Widgy.View.extend({
    template: 'edit_text_content',

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

  var App = Backbone.View.extend({
    initialize: function() {
      var page = this.options.page,
          content = page.root_node.content;

      var layout = createContent(content);
      var layout_view = this.layout_view = createNode(layout);

      this.$el.append(layout_view.widgyRender().el);
    }
  });

  var startApp = function(page) {
    app = new App({page: page, el: $('#app')});
  };
