if ( typeof window.console == 'undefined' )
{
  var $console = $('<ul class="console" style="margin-bottom: 100px"></ul>');
  $(document.body).append($console);
  window.console = {
    log: function(what) {
      $console.append($('<li/>').text(what));
    }
  };
}

require.config({
  // ordered dependencies (example: jquery plugins)
  shim: {
    'underscore': {
      exports: '_'
    },
    'backbone': {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    }
  },
  paths: {
  'jquery': './lib/jquery',
  'underscore': './lib/underscore',
  'backbone': './lib/backbone',
  'mustache': './lib/mustache',
  'text': 'require/text'
  }
});
