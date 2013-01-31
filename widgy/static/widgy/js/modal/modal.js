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
    var data = JSON.parse(resp.responseText);
    var message;
    if ( data.message )
       message =  data.message;
    else if ( resp.status == 404 )
      message = 'Try refreshing the page';
    else
      message = 'Unkown error';

    var error_view = new ErrorView({
      message: message
    });
    $(document.body).append(error_view.render().$el.css({
      left: $(window).width()/2,
      top: $(window).height()/2,
      position: 'fixed'
    }));
  };

  return {
    raiseError: raiseError
  };
});
