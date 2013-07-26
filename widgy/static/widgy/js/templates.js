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
    return Q(Backbone.ajax({url: template_id, cache: false}))
      .then(function(template) {
        var model = new Template(_.extend({url: template_id}, template));
        return model;
      })
      .fail(modal.ajaxError);
  };

  return {
    getTemplate: getTemplate
  };
});
