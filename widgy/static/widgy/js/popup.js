jQuery(function($) {
  // show/hide publish at calendar fields according to what the publish_radio
  // field dictates.
  var $publish_at = $('.publish_at_container');
  function showHideCalendar() {
    var publish_now = $('[name=publish_radio]:checked').val() == 'now';

    if ( publish_now ) {
      $publish_at.hide();
    } else {
      $publish_at.show();
    }
  }
  $('[name=publish_radio]').on('change', showHideCalendar);
  showHideCalendar();

  // Loading spinner
  $('.popUp form [type=submit]').click(function() {
    $(this).addClass('loading');
  });
  $('.popUp form').submit(function() {
    var $form = $(this);
    var $submits = $form.find('[type=submit]');
    if ( $form.find('.loading').length == 0 ) {
      $submits.first().addClass('loading');
    }
    $submits.attr('disabled', true);
  });
});
