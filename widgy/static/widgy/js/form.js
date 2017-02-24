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

    renderHTML: function(template) {
      // BBB: Django 1.9 and 1.10 attach event handlers on document ready, but
      // we need to attach them after rendering the page. In Django 1.11 the handlers
      // will attach to 'body' so this shouldn't be a problem anymore.
      //
      // See https://code.djangoproject.com/ticket/26357

      var ret = Backbone.View.prototype.renderHTML.call(this, template);

      // Only attach the handler if there isn't a similar handler attached to body
      // XXX: This should prevent this code from running on Django 1.11, but
      // this needs testing.
      var clickSelectors = _.pluck(django.jQuery._data(document.body).events.click, 'selector');
      if (!_.contains(clickSelectors, '.related-lookup')) {
        this.$el.find('.related-lookup').click(function(e) {
            e.preventDefault();
            var event = $.Event('django:lookup-related');
            $(this).trigger(event);
            if (!event.isDefaultPrevented()) {
                window.showRelatedObjectLookupPopup(this);
            }
        });
      }
      if (!_.contains(clickSelectors, '.add-another')) {
        this.$el.find('.add-another').click(function(e) {
            e.preventDefault();
            var event = $.Event('django:add-another-related');
            $(this).trigger(event);
            if (!event.isDefaultPrevented()) {
                window.showAddAnotherPopup(this);
            }
        });
      }
      return ret;
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
