;(function(Widgy) {

  var exports = Widgy.contents || (Widgy.contents = {});


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
  var Content = Widgy.Model.extend({
    urlRoot: '/admin/widgy/',

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
    },

    url: function() {
      var url = this.urlRoot + this.get('model') + '/';

      if ( ! this.isNew() ) {
        url = url + this.id + '/';
      }

      return url;
    }
  });


  /**
   * Base View for Contents.  A Content View displays the Content and also
   * provides an interface to edit it.  Usually, the ContentView just shows
   * Content and when the user wishes to edit the content, it will open another
   * view.  See `widgy.widgets.js`.
   */
  var ContentView = Widgy.View.extend({
    className: 'content',
  });


  var models = {};


  /**
   * In order to expose a Content to the rest of Widgy, you must register it.
   * This method accepts a string name and a reference to the class.  To
   * retrieve the model, you can use the `getModel` or `instantiateModel`
   * methods.
   */
  function registerModel(name, cls) {
    models[name] = cls;
  }


  /**
   * Returns a model that was registered using `registerModel`.  This method
   * accepts the name of the model you are retrieving.
   */
  function getModel(name) {
    return models[name];
  }


  /**
   * Retrieves the Content Model class based on `name` and instantiates it
   * passing in the `attrs` and `options`.
   */
  function instantiateModel(name, attrs, options) {
    var model_class = getModel(name);
    return new model_class(attrs, options);
  }


  _.extend(exports, {
    Content: Content,
    ContentView: ContentView,
    registerModel: registerModel,
    getModel: getModel,
    instantiateModel: instantiateModel
  });
})(this.Widgy);
