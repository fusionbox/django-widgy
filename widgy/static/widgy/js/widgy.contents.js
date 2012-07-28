;(function(Widgy) {

  var exports = Widgy.contents || (Widgy.contents = {});


  var Content = Backbone.Model.extend({
    urlRoot: '/admin/widgy/',

    initialize: function() {
      // debugging
      this.type = this.get('model');
    },

    url: function() {
      var url = this.urlRoot + this.get('model') + '/';

      if ( ! this.isNew() ) {
        url = url + this.id + '/';
      }

      return url;
    }
  });


  var ContentView = Widgy.View.extend({
    className: 'content',
  });


  var models = {};

  function registerModel(name, cls) {
    models[name] = cls;
  }

  function instantiateModel(name, attrs) {
    return new models[name](attrs);
  }

  _.extend(exports, {
    Content: Content,
    ContentView: ContentView,
    registerModel: registerModel,
    instantiateModel: instantiateModel
  });
})(this.Widgy);
