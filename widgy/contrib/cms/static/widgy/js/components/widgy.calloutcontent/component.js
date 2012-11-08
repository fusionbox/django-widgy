define(['widgy.contents', 'widgets/widgets',
    'underscore',
    'django_admin',
    ], function(contents, widgets,
    _,
    admin) {

  var EditorView = widgets.EditorView.extend({
    events: function(){
      return _.extend({}, widgets.EditorView.prototype.events, {
        'click [data-add_button]': 'add'
      });
    },
    initialize: function() {
      // TODO these should not be globals.
      if ( ! window.dismissAddAnotherPopup )
        window.dismissAddAnotherPopup = admin.RelatedObjectLookups.dismissAddAnotherPopup;
      if ( ! window.SelectBox )
        window.SelectBox = admin.SelectBox;
      widgets.EditorView.prototype.initialize.apply(this, arguments);
      _.bindAll(this, 'add');
    },

    add: function(event){
      return admin.RelatedObjectLookups.showAddAnotherPopup(event.currentTarget);
    }

  });

  var ContentView = widgets.WidgetView.extend({
    editorClass: EditorView
  });

  var CalloutContent = contents.Content.extend({
    viewClass: ContentView
  });

  return CalloutContent;
});
