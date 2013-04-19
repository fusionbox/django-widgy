jQuery(function($) {
  $('.tabify .tabs a').bind('click', function() {
    $('.tabify .tabs a').removeClass('active'); // clear the active tabs
    $('.tabify .tabs a[href=' + $(this).attr('href') + ']').addClass('active'); // activate the clicked tab
    $('.tabify .tabContent').removeClass('active'); // clear the active content
    $($(this).attr('href')).addClass('active'); // show the clicked content
  });

  //|
  //| If there's a #tab in the URL, CLICK ON THAT TAB!!!
  //|
  if(window.location.hash) {
    $('.tabs a[href="' + window.location.hash + '"]').click();
  }
});
