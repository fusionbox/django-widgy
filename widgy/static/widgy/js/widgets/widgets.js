define([
'widgy.backbone',
'widgy.contents',
'underscore',
'form',
'templates'
    ], function(
    Backbone,
    contents,
    _,
    form,
    templates) {

  // TODO: is Widget a good name?  We are trying to unify our vocabulary.
  
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
    events: function() {
      return _.extend({}, form.FormView.prototype.events , {
        'click .cancel': 'close'
      });
    },

    initialize: function() {
      form.FormView.prototype.initialize.apply(this, arguments);
      _.bindAll(this,
        'handleSuccess',
        'handleError',
        'renderHTML'
      );
    },

    handleError: function(model, xhr, options){
      var response,
          error_func = this['handleError' + parseInt(xhr.status, 3)];
      if (!! error_func ) {
        error_func(model, xhr, options);
      }
      response = $.parseJSON(xhr.responseText);
      $('ul.errorlist').remove();
      _.each(response, function(messages, field_name){
        var field = this.$('[name="' + field_name + '"]'),
            error_list = field.parent().find('ul.errorlist');
        if ( error_list.length <= 0 ){
          error_list = $('<ul class=errorlist>');
          field.after(error_list);
        } else {
          error_list.html('');
        }

        _.each(messages, function(msg){
          var message_li = $('<li class=error>');
          message_li.text(msg);
          error_list.append(message_li);
        });
      }, this);
    },

    render: function(event) {
      // asychronous (possibly) template rendering.
      templates.render(
          this.model.get('template_url'),
          'edit_template',
          this.toJSON(),
          this.renderHTML
          );

      return this;
    },

    renderHTML: function(html) {
      this.$el.html(html);
    },

    submit: function() {
      var values = this.serialize();

      this.model.save(values, {
        success: this.handleSuccess,
        error: this.handleError
      });
    },

    handleSuccess: function(model, response, options) {
      // kill the template cache.
      templates.remove(model.get('template_url'));
      this.close();
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
  var WidgetView = contents.ContentView.extend({
    editorClass: EditorView,

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

  // TODO: It would be nice to have field classes.  I want to define a list of
  // fields and their types and properties like required and such.  EditorView
  // subclasses could define a fields list that would be output automatically
  // in render.


  return {
    WidgetView: WidgetView,
    EditorView: EditorView
  };
});
