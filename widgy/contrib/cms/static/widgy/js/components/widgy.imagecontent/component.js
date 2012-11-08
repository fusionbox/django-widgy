define([ 'widgy.contents', 'widgets/widgets', 'underscore'
    ], function(
    contents,
    widgets,
    _) {

  var EditorView = widgets.EditorView.extend({
    events: function() {
      return _.extend({}, widgets.EditorView.prototype.events , {
        'click .upload': 'upload'
      });
    },

    initialize: function() {
      widgets.EditorView.prototype.initialize.apply(this, arguments);
      _.bindAll(this, 'upload');
    },

    upload: function(event) {
      event.preventDefault();
      var id = 'id_image_widget_' + this.cid;
      var id2=String(id).replace(/\-/g,"____").split(".").join("___");
      FBWindow = window.open('/admin/media-library/browse/?pop=1&type=Image', id2, 'height=600,width=1000,resizable=yes,scrollbars=yes');
      FBWindow.focus();
    },

    toJSON: function() {
      var json = widgets.EditorView.prototype.toJSON.call(this, arguments);
      json.cid = this.cid;
      json.input_id = 'id_image_widget_' + this.cid;
      return json;
    }
  });

  var ContentView = widgets.WidgetView.extend({
    editorClass: EditorView,
  });

  var ImageContent = contents.Content.extend({
    viewClass: ContentView
  });

  return ImageContent;
});
