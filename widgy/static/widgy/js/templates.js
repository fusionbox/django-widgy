define([
    'widgy.backbone',
    'underscore'
    ], function(
      Backbone,
      _
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

  var render = function(template_id, type, context, callback) {
    var template = templates.get(template_id);

    if (template) {
      callback(template.render(type, context, callback));
    } else {
      template = new Template({url: template_id});

      template.fetch({
        success: function(model) {
          templates.add(model);
          callback(model.render(type, context));
        },
        cache: false
      });
    }
  };

  var remove = function(template_id) {
    var template = templates.get(template_id);

    if ( template )
      templates.remove(template);
  };

  return {
    render: render,
    remove: remove
  };
});
