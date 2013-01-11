define([ 'jquery', 'underscore', 'backbone', 'mustache' ], function($, _, Backbone, Mustache) {

  Mustache.tags = ['<%', '%>'];

  var renderTemplate = function(template, context) {
      return Mustache.render(template, context);
  };

  /**
   * Our base Backbone classes.
   */
  var View = Backbone.View.extend({
    triggers: {},

    /**
     * Please remember to call super:
     *
     * Backbone.View.prototype.initialize.apply(this, arguments);
     */
    initialize: function() {
      _.bindAll(this,
        'close',
        'render',
        'toJSON',
        'bubble'
      );
    },

    /**
     * These are DOM Events that just trigger an event on the View.
     * 
     * Inspired by Derick Bailey's Backbone.Marionette:
     * https://github.com/derickbailey/backbone.marionette/blob/master/src/backbone.marionette.view.js#L70
     */
    configureTriggers: function() {
      var events = {};
      _.each(this.triggers, function(value, key) {
        events[key] = function(event) {
          if ( event ) {
            if ( event instanceof $.Event ) {
              event.preventDefault();
              event.stopPropagation();
            }
            this.trigger(value, this);
          }
        };
      });

      return events;
    },

    /**
     * Copied from Derick Bailey's Backbone.Marionette:
     * https://github.com/derickbailey/backbone.marionette/blob/master/src/backbone.marionette.view.js#L97
     */
    delegateEvents: function(events) {
      events = events || this.events;
      if (_.isFunction(events)) {
        events = events.call(this);
      }

      var combinedEvents = {};
      var triggers = this.configureTriggers();
      _.extend(combinedEvents, events, triggers);

      Backbone.View.prototype.delegateEvents.call(this, combinedEvents);
    },

    /**
     * Adds a method for killing zombies.
     *
     * Based on Derick Bailey's blog post:
     * http://lostechies.com/derickbailey/2011/09/15/zombies-run-managing-page-transitions-in-backbone-apps/
     */
    close: function(event) {
      if ( event && event.preventDefault ) {
        event.preventDefault();
      }

      this.remove();
      this.undelegateEvents();
      this.onClose();
      this.trigger('close', this);
    },

    onClose: function() {},

    /**
     * If your subclass has a template property, render will use Mustache to
     * render the template and passes in a context that is retrieved using
     * `View.toJSON`.
     */
    template: false,

    getTemplate: function() {
      return this.template;
    },

    render: function() {
      var context = this.toJSON();

      this.$el.html(this.renderTemplate(this.getTemplate(), context));

      return this;
    },

    // TODO: caching templates?
    renderTemplate: renderTemplate,

    toJSON: function() {
      return this.model ? this.model.toJSON() : {};
    },

    bubble: function(event) {
      this.trigger.apply(this, arguments);
    }
  });


  /**
   * None of our models use ids, they all use URLs to communicate with the
   * server.  See `widgy/models.py` for more on how to expose the URL.
   */
  var Model = Backbone.Model.extend({
    idAttribute: 'url',

    url: function() {
      if ( ! this.id ) {
        return Backbone.Model.prototype.url.apply(this, arguments);
      } else {
        return this.id;
      }
    }
  });


  /**
   * Maintains an app "global" list of Views so that you can find them using
   * their properties, such as their `el` or their model's id.
   *
   * The AppView has an instance of this list to keep track of all of the node
   * views.
   * 
   * This is analogous to a Collection for Views.
   */
  function ViewList() {
    this.list = [];

    _.bindAll(this,
      'remove',
      'push'
    );
  }

  _.extend(ViewList.prototype, {
    push: function(view) {
      view.on('close', this.remove);
      this.list.push(view);
    },

    remove: function(view) {
      view.off('close', this.remove);

      var index = _.indexOf(this.list, view);

      if ( index >= 0 ) {
        return this.list.splice(index, 1);
      } else {
        return false;
      }
    },

    closeAll: function() {
      return _.each(_.clone(this.list), function(view) {
        return view.close();
      });
    },

    findById: function(id) {
      return this.find(function(view) {
        return id === view.model.id;
      });
    },

    findByEl: function(el) {
      return this.find(function(view) {
        return el === view.el;
      });
    }
  });

  // mixin some underscore methods.
  var methods = [
    'each', 'find', 'contains'
    ];

  _.each(methods, function(method) {
    ViewList.prototype[method] = function() {
      return _[method].apply(_, [this.list].concat(_.toArray(arguments)));
    };
  });


  return _.extend({}, Backbone, {
    Model: Model,
    View: View,
    ViewList: ViewList,
    renderTemplate: renderTemplate
  });
});
