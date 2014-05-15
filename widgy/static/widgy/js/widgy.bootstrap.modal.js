requirejs.config({
  paths: {
    'bootstrap': './lib/bootstrap.modal'
  },

  shim: {
    'bootstrap': {
      deps: [ 'jquery' ],
      exports: 'jquery',
    }
  },
});

define([ 'jquery', 'bootstrap' ], function($) {
  $('.myModal').modal('show');
});
