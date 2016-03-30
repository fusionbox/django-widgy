/* adapted from
 * http://zogovic.com/post/21784525226/simple-html5-details-polyfill
 */
jQuery(function($) {
  var supported = 'open' in document.createElement('details');

  if ( ! supported ) {
    $(document.body).addClass('no-details');
    $('summary').on('click', function(event) {
      var $details = $(this).closest('details');
      if ( $details.attr('open') || $details.hasClass('open') )
        $details.removeAttr('open').removeClass('open');
      else
        $details.attr('open', true).addClass('open');
    });
    return false;
  }
});
