jQuery(function ($) {
  // wymeditor requires that it have a script tag in the dom
  var script = document.createElement('script');
  script.src = '/static/wymeditor/jquery.wymeditor.js'
  var s = $('script:first')[0]
  s.parentNode.insertBefore(script, s);

  setTimeout(function () {
    $(".WYMEditor").wymeditor({
      updateSelector: "input:submit",
      updateEvent: "click",
      logoHtml: '',
      skin: 'twopanels',
      classesItems: [
        {'name': 'image', 'title': 'DIV: Image w/ Caption', 'expr': 'div'},
        {'name': 'caption', 'title': 'P: Caption', 'expr': 'p'},
        {'name': 'align-left', 'title': 'Float: Left', 'expr': 'p, div, img'},
        {'name': 'align-right', 'title': 'Float: Right', 'expr': 'p, div, img'}
      ]
    });
  }, 0);
})(jQuery);
