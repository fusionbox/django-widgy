define([ 'widgy.backbone' ], function(Backbone) {

  /**
   * Base Model for Contents.  A Content holds the non-structure data for a
   * Node.  While all nodes use the same class, Contents differ based on the
   * Node content type.  As such, we need a special method for accessing
   * Content Model.
   *
   * When you write a Content Model, you need to register that model using
   * `Widgy.contents.registerModel`.  This way other parts of Widgy have access
   * to the custom Content Model.  You must provide a viewClass property on
   * your Content Model in for NodeView to know which ContentView to render.
   */
  var Content = Backbone.Model.extend({
    viewClass: false,

    initialize: function() {
      // debugging: this will go away later probably.
      this.type = this.get('model');
    },

    getViewClass: function() {
      if ( ! this.viewClass ) {
        throw new Error('You need to set a viewClass property on your Content Models');
      }

      return this.viewClass;
    }
  });


  /**
   * Base View for Contents.  A Content View displays the Content and also
   * provides an interface to edit it.  Usually, the ContentView just shows
   * Content and when the user wishes to edit the content, it will open another
   * view.  See `widgy.widgets.js`.
   */
  var ContentView = Backbone.View.extend({
    className: 'content'
  });


  /**
   * Returns a Model class that was fetched.  This method accepts the name of
   * the model you are retrieving.
   */
  function getModel(name, cb) {
    var deps = [ 'components/' + name + '/component' ];
    require(deps, cb);
  }


  return {
    Content: Content,
    ContentView: ContentView,
    getModel: getModel
  };
});
