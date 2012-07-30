define([ 'jquery', 'backbone', 'mustache' ], function($, Backbone, Mustache) {

  /**
   * Our base Backbone classes.
   */
  var View = Backbone.View.extend({
    constructor: function() {
      Backbone.View.prototype.constructor.apply(this, arguments);
    },

    initialize: function() {
      _.bindAll(this,
        'close',
        'render'
      );
    },

    /**
     * Adds a method for killing zombies.
     *
     * Based on Derick Bailey's blog post:
     * http://lostechies.com/derickbailey/2011/09/15/zombies-run-managing-page-transitions-in-backbone-apps/
     */
    close: function(event) {
      if ( event ) {
        event.preventDefault();
      }

      this.remove();
      this.undelegateEvents();
      this.onClose();
      this.trigger('close', this);
    },

    onClose: function() {},

    /**
     * If your subclass has a template property, render will use ICanHaz to
     * render the template and passes in `model.toJSON()`.
     */
    template: false,

    render: function() {
      if (this.template) {
        var context = this.model ? this.model.toJSON() : {};
        this.$el.html(this.renderTemplate(this.template, context));
      }

      return this;
    },

    // TODO: caching templates?
    renderTemplate: function(template, context) {
      var m =  $(Mustache.render(template, context));
      return m;
    }
  });


  /**
   * None of our models use ids, they all use URLs to communicate with the
   * server.  See `widgy/models.py` for more on how to expose the URL.
   */
  var Model = Backbone.Model.extend({
    idAttribute: 'url',

    url: function() {
      return this.id;
    }
  });


  /**
   * Maintains an app "global" list of Views so that you can find them using
   * their properties, such as their `el` or their model's id.
   *
   * The AppView has an instance of this list to keep track of all of the node
   * views.
   */
  function ViewList() {
    this.list = []
  }

  _.extend(ViewList.prototype, {
    push: function(view) {
      this.list.push(view);
    },

    each: function(iterator, context) {
      return _.each(this.list, iterator, context);
    },

    find: function(finder) {
      return _.find(this.list, finder);
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


  return _.extend({}, Backbone, {
    Model: Model,
    View: View,
    ViewList: ViewList
  });
});
