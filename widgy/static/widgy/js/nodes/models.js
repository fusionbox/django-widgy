define([ 'underscore', 'widgy.backbone',
    'widgy.contents'
    ], function(
      _, Backbone,
      contents
      ) {

  /**
   * Asynchronously fetches a component.
   */
  function getComponent(name, cb) {
    var deps = [ 'components/' + name + '/component' ];
    require(deps, cb);
  }


  /**
   * Nodes provide structure in the tree.  Nodes only hold data that deals with
   * structure.  Any other data lives in its content.
   *
   * A node will have two properties: `children` and `content`.  `children` is
   * a NodeCollection which is basically just a list of child nodes. `content`
   * is model containing all non-structure information about a node.  The
   * actual Model Class that defines the content property depends on the
   * content type.  See `widgy.contents.js` for more information.
   */
  var Node = Backbone.Model.extend({
    urlRoot: '/admin/widgy/node/',

    constructor: function() {
      this.children = new NodeCollection(null, {
        parent: this
      });

      Backbone.Model.apply(this, arguments);
    },

    initialize: function() {
      Backbone.Model.prototype.initialize.apply(this, arguments);

      _.bindAll(this,
        'instantiateContent',
        'trigger'
        );
    },

    parse: function(response) {
      if ( response.node ) {
        return response.node;
      } else {
        return response;
      }
    },

    set: function(key, val, options) {
      var attrs;

      // Handle both `"key", value` and `{key: value}` -style arguments.
      if (_.isObject(key)) {
        attrs = key;
        options = val;
      } else {
        (attrs = {})[key] = val;
      }

      var children = attrs.children,
          content = attrs.content;

      delete attrs.children;
      delete attrs.content;

      var ret = Backbone.Model.prototype.set.call(this, attrs, options);

      if (ret) {
        if (children) {
          this.children.update2(children, options);
          if ( options && options.resort ) {
            this.children.sortByRight();
          }
        }
        if (content) this.loadContent(content);
      }

      return ret;
    },

    url: function() {
      if ( this.id ) {
        return this.id;
      }
      return this.urlRoot;
    },

    loadContent: function(content) {
      if ( this.content ) {
        console.log(this.__class__, 'updating content', content);

        this.content.set(content);
      } else if ( content ) {
        console.log(this.__class__, 'go load my content model');

        // we store these variables because we need them now.
        this.pop_out = content.pop_out;
        this.shelf = content.shelf;
        this.__class__ = content.__class__;
        this.css_classes = content.css_classes;

        // This is asynchronous because of requirejs.
        getComponent(content.component, _.bind(this.instantiateContent, this, content));
      }
    },

    instantiateContent: function(content, component) {
      console.log(this.__class__, 'instantiating content');

      this.content = new component.Model(content, {
        node: this
      });

      this.content.__view_class = component.View;

      this.trigger('load:content', this.content);
    },

    sync: function(method, model, options) {
      // Provides an optimization for refreshing the shelf compatibility.
      // Previously, when editing a node, you had to do two requests (one for
      // the node, one for the shelf compatibility) to update the UI.  In
      // addition, the shelf request had to happen after the node one, to
      // prevent getting the compatibility wrong.  This refreshes compatibility
      // in one request instead of waiting for two round trips.
      var old_success = options.success;

      options.success = function(resp, status, xhr) {
        if ( old_success ) old_success(resp, status, xhr);

        if ( options.app && resp.compatibility ) {
          options.app.setCompatibility(resp.compatibility);
        }
      };

      if ( options.app )
      {
        var model_url = _.result(model, 'url'),
            root_url = _.result(options.app.root_node_view.model, 'url');

        options.url =  model_url + '?include_compatibility_for=' + root_url;
      }

      Backbone.sync.call(this, method, model, options);
    }
  });


  /**
   * NodeCollections provide the children interface for nodes and also an
   * interface to NodeViews for how to handle child NodeViews.
   */
  var NodeCollection = Backbone.Collection.extend({
    model: Node,

    initialize: function(models, options) {
      Backbone.Collection.prototype.initialize.apply(this, arguments);

      if ( options ) {
        this.parent = options.parent;
      }
    },

    /**
     * For each model in the new data, if
     *    - the model exists, update the data of that model.
     *    - the model is new, create a new instance and add it to the
     *      collection.
     *    - else, remove the old model from the collection.
     */
    update2: function(data, options) {
      var models = [];

      _.each(data, function(child) {
        var existing = this.get(child.url);

        if ( existing ) {
          existing.set(child, options);
          models.push(existing);
        } else {
          models.push(child);
        }
      }, this);

      this.update(models, options);
    },

    /**
     * Sort based on the right_ids.  This will most likely fail if the
     * right_ids are not up to date, so please only call this after updating
     * the whole collection.
     */
    sortByRight: function(options) {
      var new_order = [],
          right_id = null;

      while (new_order.length < this.models.length) {
        var has_right = this.where({right_id: right_id})[0];
        new_order.unshift(has_right);

        right_id = has_right.id;
      }

      this.models = new_order;

      if (!options || !options.silent) this.trigger('sort', this, options);
      return this;
    }
  });


  return {
    Node: Node,
    NodeCollection: NodeCollection
  };

});
