(function(Widgy) {

  var exports = Widgy.widgets || (Widgy.widgets = {});
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
  var WidgetView = Widgy.contents.ContentView.extend({
    editorClass: false,

    events: {
      'click .edit': 'editWidget'
    },

    initialize: function() {
      this.model.on('change', this.render);
    },

    getEditorClass: function() {
      return this.editorClass;
    },

    editWidget: function(event) {
      event.preventDefault();

      var editor_class = this.getEditorClass(),
          edit_view = new editor_class({model: this.model});

      edit_view.on('close', this.render)
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
  var EditorView = Widgy.View.extend({
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

  // TODO: It would be nice to have field classes.  I want to define a list of
  // fields and their types and properties like required and such.  EditorView
  // subclasses could define a fields list that would be output automatically
  // in render.


  _.extend(exports, {
    WidgetView: WidgetView,
    EditorView: EditorView
  });
})(this.Widgy);
