define([
    'jquery',
    'widgy.backbone',
    'underscore'
    ], function(
      $,
      Backbone,
      _) {

  $.fn.getValue = function() {
    if ( window.CKEDITOR && window.CKEDITOR.instances[this[0].id] ) {
      return window.CKEDITOR.instances[this[0].id].getData();
    }
    return this.val() || '';
  };

  $.fn.serializeObject = function() {
    var ret = {};
    this.each(function() {
      var name = this.name;

      if (! name || (_.contains(['checkbox', 'radio'], this.type) && ! this.checked))
        return;

      if (_.contains(ret, name)) {
        if (!ret[name].push) {
          ret[name] = [ret[name]];
        }
        ret[name].push($(this).getValue()); 
      } else {
        ret[name] = $(this).getValue();
      }
    });
    return ret;
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

    close: function() {
      if (window.CKEDITOR) {
        this.$('.widgy_ckeditor').each(function() {
          var editor = window.CKEDITOR.instances[this.id];
          if (editor) editor.destroy();
        });
      }
      Backbone.View.prototype.close.apply(this, arguments);
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
