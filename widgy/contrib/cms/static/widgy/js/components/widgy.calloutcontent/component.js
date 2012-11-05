define(['widgy.contents', 'widgets/widgets',
    'underscore',
    'django_admin',
    'text!./content.html',
    'text!./edit.html'
    ], function(contents, widgets,
    _,
    admin,
    content_template,
    edit_template) {

  var EditorView = widgets.EditorView.extend({
    template: edit_template,
    events: function(){
      return _.extend({}, widgets.EditorView.prototype.events, {
        'click [data-add_button]': 'add'
      });
    },
    initialize: function() {
      if ( ! window.dismissAddAnotherPopup )
        window.dismissAddAnotherPopup = admin.RelatedObjectLookups.dismissAddAnotherPopup;
      if ( ! window.SelectBox )
        window.SelectBox = admin.SelectBox;
      widgets.EditorView.prototype.initialize.apply(this, arguments);
      _.bindAll(this, 'add');
    },

    add: function(event){
      return admin.RelatedObjectLookups.showAddAnotherPopup(event.currentTarget);
    },

    toJSON: function() {
      var json = widgets.EditorView.prototype.toJSON.call(this, arguments);
      json.cid = this.cid;
      json.input_id = 'id_callout_widget_' + this.cid;
      return json;
    }

  });

  var ContentView = widgets.WidgetView.extend({
    template: content_template,
    editorClass: EditorView
  });

  var CalloutContent = contents.Content.extend({
    viewClass: ContentView
  });

  return CalloutContent;
});
