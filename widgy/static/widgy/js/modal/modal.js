define([ 'widgy.backbone',
    'text!./modal.html'
    ], function(Backbone,
      modal_template
      ) {

  var ModalView = Backbone.View.extend({
    tagName: 'div',
    template: modal_template,
    events: {
      'click .close': 'close',
      'click .overlay': 'close'
    },

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);

      this.message = options.message;
    },

    toJSON: function() {
      return {
        message: this.message
      };
    }
  });


  var ErrorView = ModalView.extend({
    className: 'errorMessage'
  });

  var raiseError = function(model, resp, options) {
    var error_view = new ErrorView({
      message: JSON.parse(resp.responseText).message
    });
    $(document.body).append(error_view.render().$el.css({
      left: document.body.offsetWidth/2,
      top: document.body.offsetHeight/2,
      position: 'fixed'
    }));
  };

  return {
    raiseError: raiseError
  };
});
