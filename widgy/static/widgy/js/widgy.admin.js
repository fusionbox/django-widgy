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
