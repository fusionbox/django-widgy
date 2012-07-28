;(function() {

  var EditTextContentView = Widgy.widgets.EditorView.extend({
    template: 'edit_text_content'
  });

  var TextContentView = Widgy.widgets.WidgetView.extend({
    template: 'text_content',
    editorClass: EditTextContentView
  });

  var TextContent = Widgy.contents.Content.extend({
    viewClass: TextContentView
  });

  Widgy.contents.registerModel('TextContent', TextContent);

})();
