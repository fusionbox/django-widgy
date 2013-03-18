define([
'underscore',
'widgy.backbone',
'lib/q',
'widgy.contents',
'nodes/nodes',
'form',
'templates'
    ], function(
    _,
    Backbone,
    Q,
    contents,
    nodes,
    form,
    templates) {


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
      // kill the template cache.
      templates.remove(model.get('template_url'));
      this.close();
    },

    handleError: function(model, xhr, options){
      var response,
          error_func = this['handleError' + parseInt(xhr.status, 3)];
      if (!! error_func ) {
        error_func(model, xhr, options);
      }

      this.spinner.restore();
      response = $.parseJSON(xhr.responseText);
      $('ul.errorlist').remove();
      _.each(response, function(messages, field_name){
        var error_list = $('<ul class="errorlist">');

        if ( field_name === '__all__' ) {
          this.$el.prepend(error_list);
        } else {
          this.$('[name="' + field_name + '"]').parent().prepend(error_list);
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
  var WidgetView = contents.View.extend({
    editorClass: EditorView,

    events: Backbone.extendEvents(contents.View, {
      'click .edit': 'editWidget'
    }),

    getEditorClass: function() {
      return this.editorClass;
    },

    editWidget: function(event) {
      event.preventDefault();

      var editor_class = this.getEditorClass(),
          edit_view = new editor_class({
            app: this.app,
            model: this.content
          }),
          widget = this;

      new Backbone.Spinner({el: this.$el.find('.edit:first')});

      this.listenTo(edit_view, 'close', this.rerender);

      edit_view.renderPromise()
        .then(function(edit_view) {
          widget.$preview.html(edit_view.el);
          widget.$('.edit:first').remove();

          // TODO: use HTML autofocus property??
          edit_view.$(':input:first').focus();
        })
        .done();
    }
  });


  return _.extend({}, contents, {
    View: WidgetView,
    EditorView: EditorView
  });
});
