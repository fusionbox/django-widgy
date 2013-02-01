var requirejs, jsdom, setup;
requirejs = require('requirejs');
jsdom = require('jsdom').jsdom;

global.document = global.document || jsdom();
global.window = global.window = global.document.createWindow();

// Does this matter? Backbone needs this set
global.location = {
  href: '//127.0.0.1'
}

requirejs.config({
  baseUrl: "widgy/static/widgy/js/",
  shim: {
    'underscore': {
      exports: '_'
    },
    'backbone': {
      deps: ['underscore', 'jquery', 'csrf'],
      exports: 'Backbone'
    },
    'csrf': {
      deps: ['jquery'],
      exports: 'csrf'
    }
  },
  paths: {
  'jquery': 'lib/jquery',
  'underscore': 'lib/underscore',
  'backbone': 'lib/backbone',
  'mustache': 'lib/mustache',
  'csrf': 'lib/csrf',
  'django_admin' : 'lib/django_admin',
  'text': 'require/text'
  }
});

test = {

  create: function(){
    document.innerHTML = '<html><head></head><body></body></html>';
  },
  
  destroy: function(){
    document.innerHTML = '';
  },

};

module.exports = {
  test: test
};
