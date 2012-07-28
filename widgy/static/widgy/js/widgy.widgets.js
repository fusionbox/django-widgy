(function(Widgy) {

  var exports = Widgy.widgets || (Widgy.widgets = {});


  var WidgetView = Widgy.contents.ContentView.extend({
    events: {
      'click .edit': 'editWidget'
    },

    initialize: function() {
      this.model.on('change', this.render, this);
    },

    editWidget: function(event) {
      event.preventDefault();

      var edit_view = new this.editorClass({model: this.model});
      edit_view.on('close', this.render)
      this.$el.html(edit_view.render().el);
    }
  });
  
  
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


  _.extend(exports, {
    WidgetView: WidgetView,
    EditorView: EditorView
  });
})(this.Widgy);
