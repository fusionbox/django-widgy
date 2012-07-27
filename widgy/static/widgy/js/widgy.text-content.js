;(function() {

  var TextContent = Widgy.contents.TextContent = Widgy.contents.ContentModel.extend({
    viewClass: 'TextContentView'
  });


  var TextContentView = Widgy.nodes.TextContentView = Widgy.nodes.WidgetView.extend({
    template: 'text_content',
    editorClass: 'EditTextContentView'
  });

  var EditTextContentView = Widgy.editors.EditTextContentView = Widgy.editors.EditorView.extend({
    template: 'edit_text_content'
  });


})();
