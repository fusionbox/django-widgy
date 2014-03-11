define([
    'underscore',
    'jquery',
    'widgy.backbone',
    'lib/q',
    'nodes/nodes',
    'form',
    'modal/modal',
    'templates'
    ], function(
      _,
      $,
      Backbone,
      Q,
      nodes,
      form,
      modal,
      templates
      ) {

  /**
   * Base Model for Contents.  A Content holds the non-structure data for a
   * Node.  While all nodes use the same class, Contents differ based on the
   * Node content type.  As such, we need a special method for accessing
   * Content Model.
   **/
  var Content = Backbone.Model.extend({
    initialize: function(attributes, options) {
      Backbone.Model.prototype.initialize.apply(this, arguments);

      // debugging: this will go away later probably.
      this.type = this.get('model');
      this.node = options.node;
    },

    isEditable: function() {
      return !!this.get('edit_url');
    }
  });


  /**
   * An EditorView provides a quick form editing interface for widgets.  It
   * assumes you have one form inside the editor.  When that form is submitted,
   * the EditorView will serialize the data from the form using `hydrateForm`
   * (which could be overwritten) and the saves those values to a model.
   *
   * Additionally, if you provide an element with a class `cancel`, the
   * EditorView will close if that element is clicked.
   */
  var EditorView = form.FormView.extend({
    className: 'widget_editor',

    events: Backbone.extendEvents(form.FormView, {
      'click .cancel': 'close'
    }),

    initialize: function() {
      form.FormView.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'handleSuccess',
        'handleError',
        'renderHTML'
      );
    },

    getTemplate: function() {
      return templates.getTemplate(this.model.get('template_url')).then(function(template) {
        return template.get('edit_template');
      });
    },

    submit: function() {
      this.spinner = new Backbone.Spinner({el: this.$el.find('[type=submit]')});

      var values = this.serialize();

      this.model.save({'attributes': values}, {
        success: this.handleSuccess,
        error: this.handleError
      });
    },

    handleSuccess: function(model, response, options) {
      this.close();
    },

    getPrefixedFieldName: function(name) {
      return this.model.get('form_prefix') + '-' + name;
    },

    removeFieldNamePrefix: function(name) {
      var prefix = this.model.get('form_prefix') + '-';
      if ( name.indexOf(prefix) === 0 ) {
        name = name.slice(prefix.length);
      }
      return name;
    },

    serialize: function() {
      var ret = {},
          prefixed = form.FormView.prototype.serialize.apply(this, arguments);

      _.map(prefixed, function(value, key) {
        ret[this.removeFieldNamePrefix(key)] = value;
      }, this);

      return ret;
    },

    handleError: function(model, xhr, options){
      var response,
          error_func = this['handleError' + parseInt(xhr.status, 3)];
      if (!! error_func ) {
        error_func(model, xhr, options);
      }

      this.spinner.restore();
      response = $.parseJSON(xhr.responseText);
      this.$('ul.errorlist').remove();
      this.$('.formField.error').removeClass('error');
      _.each(response, function(messages, field_name){
        var error_list = $('<ul class="errorlist">');

        if ( field_name === '__all__' ) {
          this.$el.prepend(error_list);
        } else {
          this.$('[name="'+ this.getPrefixedFieldName(field_name) +'"]').parent()
            .addClass('error')
            .append(error_list);
        }

        _.each(messages, function(msg){
          var message_li = $('<li class=error>');
          message_li.text(msg);
          error_list.append(message_li);
        });
      }, this);
    }
  });


  /**
   * Base Class for WidgetViews.  A WidgetView is just a specialized
   * ContentView that assumes it will have an accompanying EditorView.  Every
   * WidgetView must have an `editorClass` property, which is a reference to
   * the EditorView class.
   *
   * If you provide something with a class of `edit`, the WidgetView will bind
   * to click on it.  The default behavior is to replace the content of the
   * WidgetView with the EditorView.  When the EditorView closes, the
   * WidgetView will re-render itself.
   */
  var WidgetView = nodes.NodeView.extend({
    editorClass: EditorView,

    events: Backbone.extendEvents(nodes.NodeView, {
      'click .edit': 'editWidget'
    }),

    getEditorClass: function() {
      return this.editorClass;
    },

    editWidget: function(event) {
      event.preventDefault();
      event.stopPropagation();
      if (! this.content.isEditable())
        return;

      var editor_class = this.getEditorClass(),
          edit_view = new editor_class({
            app: this.app,
            model: this.content
          }),
          widget = this;

      new Backbone.Spinner({el: this.$el.find('.edit:first')});

      this.listenTo(edit_view, 'close', this.rerender);

      widget.$preview.html(edit_view.el);
      edit_view.renderPromise()
        .then(function(edit_view) {
          widget.$('.edit:first').remove();

          // TODO: use HTML autofocus property??
          edit_view.$(':input:first').focus();
        })
        .fail(function(err) {
          modal.raiseError(err);
          edit_view.close();
        })
        .done();
    }
  });


  return {
    Model: Content,
    View: WidgetView,
    EditorView: EditorView
  };
});
