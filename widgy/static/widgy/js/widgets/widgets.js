define([
'widgy.backbone',
'widgy.contents',
'underscore',
'text!./widget.html'
    ], function(
    Backbone,
    contents,
    _,
    widget_layout) {

  // TODO: is Widget a good name?  We are trying to unify our vocabulary.


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
  var WidgetView = contents.ContentView.extend({
    editorClass: false,
    layout: widget_layout,

    events: {
      'click .edit': 'editWidget'
    },

    initialize: function() {
      contents.ContentView.prototype.initialize.apply(this, arguments);

    },

    getEditorClass: function() {
      return this.editorClass;
    },

    editWidget: function(event) {
      event.preventDefault();

      var editor_class = this.getEditorClass(),
          edit_view = new editor_class({model: this.model});

      edit_view.on('close', this.render);
      this.$el.html(edit_view.render().el);
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
  var EditorView = Backbone.View.extend({
    events: {
      'submit form': 'handleForm',
      'click .cancel': 'close'
    },

    initialize: function() {
      Backbone.View.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'handleSuccess',
        'handleError'
      );
      this.template = this.model.get('edit_template');
    },

    handleError: function(model, xhr, options){
      var response,
          error_func = this['handleError' + parseInt(xhr.status, 3)];
      if (!! error_func ) {
        error_func(model, xhr, options);
      }
      response = $.parseJSON(xhr.responseText);
      (function(self){
        _.each(response, function(messages, field_name){
          var field = self.$('form').find('[name="' + field_name + '"]'),
              error_list = field.parent().find('ul.errors').first();
          if ( error_list.length <= 0 ){
            error_list = $('<ul class=errors>');
            field.before(error_list);
          } else {
            error_list.html('');
          }

          _.each(messages, function(msg){
            var message_li = $('<li class=error>');
            message_li.text(msg);
            error_list.append(message_li);
          });
        });
      })(this);
    },

    handleForm: function(event) {
      event.preventDefault();
      var values = this.hydrateForm();

      this.model.save(values, {
        success: this.handleSuccess,
        error: this.handleError
      });
    },

    handleSuccess: function(model, response, options) {
      this.close();
    },

    hydrateForm: function() {
      return this.$('form').serializeObject();
    }
  });

  // TODO: It would be nice to have field classes.  I want to define a list of
  // fields and their types and properties like required and such.  EditorView
  // subclasses could define a fields list that would be output automatically
  // in render.


  return {
    WidgetView: WidgetView,
    EditorView: EditorView
  };
});
