var path = require('path'),
    requirejs = require('requirejs'),
    jsdom = require('jsdom').jsdom;

require('mocha-as-promised')();

global.document = global.document || jsdom();
global.window = global.window = global.document.createWindow();

requirejs.config({
  baseUrl: path.join(__dirname, "../../widgy/static/widgy/js/"),
  paths: {
    'text': 'require/text'
  }
});

// Backbone expects window.jQuery to be set.
var Backbone = requirejs('backbone'),
    jQuery = requirejs('jquery');

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

module.exports = {
  test: test
};
