define([
    'jquery',
    'widgy.backbone',
    'widgy.contents',
    'underscore',
    'templates'
    ], function(
      $,
      Backbone,
      contents,
      _,
      templates) {

  $.fn.serializeObject = function()
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

  var FormView = Backbone.View.extend({
    events: {
      'click input[type=submit], button[type=submit]': 'handleClick',
      // TODO: make sure this works with whatever
      'keydown :input:not(textarea):not(select)': 'handleKeypress'
    },

    handleClick: function(event) {
      if ( event.target.disabled )
        return false;

      switch(event.which) {
        case 0:
          // this is 0 in ie sometimes. http://bugs.jquery.com/ticket/13209
          /* falls through */
        case 1:
          // left click, submit the form
          this.submit();
          /* falls through */
        case 2:
          // left or middle click, prevent default
          return false;
        default:
          // right click, continue as normal
          return true;
      }
    },

    handleKeypress: function(event) {
      if (event.which == 13) {
        // enter key, submit the form by clicking the submit button
        this.$el.find(':submit:not(:disabled):first').trigger({
          type: 'click',
          which: 1
        });
        return false;
      }
    },

    serialize: function() {
      return this.$el.find(':input').serializeObject();
    },

    submit: function() {}
  });

  return {
    FormView: FormView
  };
});
