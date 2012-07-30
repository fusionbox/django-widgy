define([ 'widgy.contents', 'widgy.widgets',
    'text!components/textcontent/text_content.html',
    'text!components/textcontent/edit_text_content.html'
    ], function(contents, widgets,
      text_content_template, edit_text_content_template) {

  var EditTextContentView = widgets.EditorView.extend({
    template: edit_text_content_template
  });

  var TextContentView = widgets.WidgetView.extend({
    template: text_content_template,
    editorClass: EditTextContentView
  });

  var TextContent = contents.Content.extend({
    viewClass: TextContentView
  });

  return TextContent;
});
