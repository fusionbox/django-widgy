var path = require('path'),
    requirejs = require('requirejs'),
    jsdom = require('jsdom').jsdom;

require('mocha-as-promised')();

global.document = global.document || jsdom();
global.window = global.window = global.document.createWindow();

requirejs.config({
  baseUrl: path.join(__dirname, "../../widgy/static/widgy/js/"),
  paths: {
    'jquery': './lib/jquery',
    'underscore': './lib/underscore',
    'backbone': './lib/backbone',
    'text': 'require/text'
  }
});

// Backbone expects window.jQuery to be set.
var Backbone = requirejs('lib/backbone'),
    jQuery = requirejs('lib/jquery');

Backbone.$ = jQuery;

// Does this matter? Backbone needs this set
global.location = {
  href: '//127.0.0.1'
};

test = {
  create: function(){
    document.innerHTML = '<html><head></head><body></body></html>';
  },
  
  destroy: function(){
    document.innerHTML = '';
  }
};

requirejs.define('components/testcomponent/component', ['widgy.contents'], function(contents) {
  var TestContent = contents.Model.extend();
  var EditorView = contents.EditorView.extend();

  var WidgetView = contents.View.extend({
    editorClass: EditorView
  });

  return _.extend({}, contents, {
    Model: TestContent,
    View: WidgetView
  });
});

module.exports = {
  test: test
};
