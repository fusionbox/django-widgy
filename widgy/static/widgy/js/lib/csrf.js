define([ 'jquery' ], function(jQuery){
  var $ = jQuery;
  // This method came from the Django docs.
  // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
  var csrftoken = (function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  })('csrftoken');

  if (!csrftoken) {
    // The CSRF token was not set, perhaps they are using
    // CSRF_COOKIE_HTTPONLY.
    csrftoken = $('[name=csrfmiddlewaretoken]').val();
  }

  if (!csrftoken) {
    console.error(
      "Widgy couldn't figure out the CSRF token. It checked two places:\n" +
      " - The csrftoken cookie (not available if CSRF_COOKIE_HTTPONLY is set" +
      " to True\n" +
      " - The csrfmiddlewaretoken hidden input provided by the csrftoken" +
      " template tag\n" +
      " If you can change neither of these problems, please open an issue on" +
      " http://github.com/fusionbox/django-widgy/issues explaining your" +
      " situation."
    );
  }

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  return {};
});
