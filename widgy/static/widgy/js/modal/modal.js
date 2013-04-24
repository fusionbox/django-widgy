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

    toJSON: function() {
      return {
        message: this.message
      };
    },

    open: function() {
      $(document.body).append(this.render().$el.css({
        left: $(window).width()/2,
        top: $(window).height()/2,
        position: 'fixed'
      }));
    }
  });


  var ErrorView = ModalView.extend({
    className: 'errorMessage',

    initialize: function(options) {
      Backbone.View.prototype.initialize.apply(this, arguments);

      this.message = options.message;
    }
  });

  function raiseError(message) {
    var error_view = new ErrorView({
      message: message
    });

    error_view.open();
  }

  function ajaxError(model, resp, options) {
    if ( _.contains(resp.getResponseHeader('content-type', 'application/json')) ) {
      var data = JSON.parse(resp.responseText);
      var message;
      if ( data.message )
         message =  data.message;
      else if ( resp.status == 404 )
        message = 'Try refreshing the page';
      else
        message = 'Unkown error';

      raiseError({message: message});
    } else {
      model = new ModalView();
      model.open();
      model.$el.html(resp.responseText);
    }
  }

  return {
    ModalView: ModalView,
    ErrorView: ErrorView,
    raiseError: raiseError,
    ajaxError: ajaxError
  };
});
