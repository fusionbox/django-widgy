jQuery(function($) {
  $('a.widgy-fancybox').fancybox({
    width: 700,
    type: 'iframe',
    onComplete: function() {
      $.fancybox.showActivity();
      $('#fancybox-frame').load(function(){
        $.fancybox.hideActivity();
      });
    }
  });
  window.closeFancybox = $.fancybox.close;
});

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
