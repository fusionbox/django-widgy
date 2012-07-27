/**
 * Fusionbox class
 * 
 * Provides helper methods and other things for working with JavaScript
 * and Django
 */

;(function($, exports, undefined) {
  var safe_methods_re = /^(GET|HEAD|OPTIONS|TRACE)$/
    , http_or_https_re = /^(\/\/|http:|https:).*/;

  var Fusionbox = function() {
    this.csrf_token = this.getCookie('csrftoken');

    // when the document is ready, call onload.
    $(this.onload);
  };

  Fusionbox.prototype = {

    onload: function() {},

    // This method came from the Django docs.
    // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
    getCookie: function(name) {
      var cookieValue;

      if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0, len = cookies.length; i < len; i++) {
          var cookie = $.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    },

    // This method came from the Django docs.
    // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
    sameOrigin: function(url) {
      // url could be relative or scheme relative or absolute
      var host = document.location.host // host + port
        , protocol = document.location.protocol
        , sr_origin = '//' + host
        , origin = protocol + sr_origin;

      // Allow absolute or scheme relative URLs to same origin
      return (url == origin || url.slice(0, origin.length + 1) == origin + '/')
        || (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/')
        // or any other URL that isn't scheme relative or absolute i.e relative.
        || !(http_or_https_re.test(url));
    },

    // This method came from the Django docs.
    // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
    safeMethod: function(method) {
      return (safe_methods_re.test(method));
    }
  };


  var fusionbox = exports.fusionbox = new Fusionbox();

  // This method came from the Django docs.
  // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
  $(document).ajaxSend(function(event, xhr, settings) {
    if (!fusionbox.safeMethod(settings.type) && fusionbox.sameOrigin(settings.url)) {
      xhr.setRequestHeader("X-CSRFToken", fusionbox.csrf_token);
    }
  });

})(jQuery, window);
