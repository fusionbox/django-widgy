define([
    'widgy.backbone',
    'underscore',
    'lib/q',
    'modal/modal'
    ], function(
      Backbone,
      _,
      Q,
      modal
      ) {

  var templates = new Backbone.Collection();

  var Template = Backbone.Model.extend({
    initialize: function() {
      Backbone.Model.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'render'
      );
    },

    render: function(type, context) {
      return Backbone.renderTemplate(this.get(type), context);
    }
  });

  var getTemplate = function(template_id) {
    var deferred = Q.defer(),
        template = templates.get(template_id);

    if ( template ) {
      deferred.resolve(template);
    } else {
      template = new Template({url: template_id});

      deferred.resolve(
        Q.when(template.fetch({cache: false}))
          .then(templates.add, modal.raiseError)
          );
    }

    return deferred.promise;
  };

  var remove = function(template_id) {
    var template = templates.get(template_id);

    if ( template )
      templates.remove(template);
  };

  return {
    getTemplate: getTemplate,
    remove: remove
  };
});
