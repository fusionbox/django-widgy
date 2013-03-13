/* adapted from
 * http://zogovic.com/post/21784525226/simple-html5-details-polyfill
 */
jQuery(function($) {
  var supported = 'open' in document.createElement('details');

  if ( ! supported ) {
    $(document.body).addClass('no-details');
    $('summary').on('click', function(event) {
      var $details = $(this).parents('details');
      if ( $details.attr('open') )
        $details.removeAttr('open');
      else
        $details.attr('open', true);
    });
  }
});
