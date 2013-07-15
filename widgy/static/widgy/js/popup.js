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
      // enter pressed
      $submits.first().addClass('loading');
    }
    // We want to disable the submit buttons to prevent double-submission, but
    // we need the data from the submit button to be submitted, which won't
    // happen if it's disabled in this frame.
    setTimeout(function() {
      $submits.attr('disabled', true);
    }, 0);
  });
});
