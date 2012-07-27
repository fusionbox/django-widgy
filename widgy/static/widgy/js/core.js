;(function() {
  var exports = window.Widgy = {};

  var View = exports.View = Backbone.View.extend({
    /**
     * Adds a method for killing zombies.
     *
     * Based on Derick Bailey's blog post:
     * http://lostechies.com/derickbailey/2011/09/15/zombies-run-managing-page-transitions-in-backbone-apps/
     */
    close: function() {
      this.remove();
      this.unbind();
      this.onClose();
    },

    onClose: function() {},

    render: function() {
      this.$el.html(ich[this.template](this.model.toJSON()));

      return this;
    }
  });


  jQuery.fn.serializeObject = function()
  {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
      if (o[this.name] !== undefined) {
        if (!o[this.name].push) {
          o[this.name] = [o[this.name]];
        }
        o[this.name].push(this.value || '');
      } else {
        o[this.name] = this.value || '';
      }
    });
    return o;
  };
})();
