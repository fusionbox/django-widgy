$('.popUp form').ajaxForm({
  target: '.popUp',
  beforeSubmit: function(data, $form) {
    // prevent submission of forms without any enabled submit buttons.
    // this is the normal behavior for a form, but ajaxForm doesn't
    // implement it.
    return $form.find('[type=submit]:not([disabled])').length >= 1;
  }
});
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
