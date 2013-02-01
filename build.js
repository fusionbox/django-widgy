({
  baseUrl: "widgy/static/widgy/js/",
  name: "widgy",
  out: "static/widgy/js/widgy-built",
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
    'jquery': './lib/jquery',
    'underscore': './lib/underscore',
    'backbone': './lib/backbone',
    'mustache': './lib/mustache',
    'csrf': './lib/csrf',
    'RelatedObjectLookups' : './lib/RelatedObjectLookups',
    'text': 'require/text'
  },
  uglify: {
    beautify: false
  }
})
