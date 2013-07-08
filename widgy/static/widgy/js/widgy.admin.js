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
