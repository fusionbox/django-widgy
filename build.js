({
  baseUrl: "widgy/static/widgy/js/",
  name: "widgy",
  out: "static/widgy/js/widgy-built",
  shim: {
    'underscore': {
      exports: '_'
    },
    'backbone': {
      deps: ['underscore', 'jquery', 'fusionbox'],
      exports: 'Backbone'
    },
    'fusionbox': {
      deps: ['jquery'],
      exports: 'fusionbox'
    }
  },
  paths: {
    'jquery': './lib/jquery',
    'underscore': './lib/underscore',
    'backbone': './lib/backbone',
    'mustache': './lib/mustache',
    'fusionbox': './lib/fusionbox',
    'text': 'require/text'
  },
  uglify: {
    beautify: false
  }
})
