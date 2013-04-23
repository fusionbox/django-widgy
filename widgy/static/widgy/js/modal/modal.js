define([ 'widgy.backbone',
    'text!./modal.html',
    'text!./error.html'
    ], function(Backbone,
      modal_template,
      error_template
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


  var HTMLModal = ModalView.extend({
    initialize: function(options) {
      ModalView.prototype.initialize.apply(this, arguments);

      this.html = options.html;
    },

    render: function() {
      ModalView.prototype.render.apply(this, arguments);
      this.$('.modal').append(this.html);
      return this;
    }
  });


  function iframe(url) {
    var modal = new HTMLModal({html: $('<iframe>').attr('src', url)});
    modal.open();

    return modal;
  }


  var ErrorView = ModalView.extend({
    className: 'errorMessage',
    template: error_template,

    initialize: function(options) {
      ModalView.prototype.initialize.apply(this, arguments);

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
      modal = new HTMLModal({html: resp.responseText});
      modal.open();
    }
  }

  return {
    ModalView: ModalView,
    ErrorView: ErrorView,
    raiseError: raiseError,
    ajaxError: ajaxError,
    iframe: iframe
  };
});
