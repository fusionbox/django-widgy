function dismissEditRelatedPopup(win, objId, newRepr) {
    objId = html_unescape(objId);
	newRepr = html_unescape(newRepr);
	var name = windowname_to_id(win.name).replace(/^edit_/, '');;
	var elem = document.getElementById(name);
	if (elem) {
		var opts = elem.options,
				l = opts.length;
		for (var i = 0; i < l; i++) {
			if (opts[i] && opts[i].value == objId) {
				opts[i].innerHTML = newRepr;
			}
		}
	}
	win.close();
};

if (!dismissAddAnotherPopup.original) {
	var originalDismissAddAnotherPopup = dismissAddAnotherPopup;
	dismissAddAnotherPopup = function(win, newId, newRepr) {
		originalDismissAddAnotherPopup(win, newId, newRepr);
		newId = html_unescape(newId);
		newRepr = html_unescape(newRepr);
		var id = windowname_to_id(win.name);
		$('#' + id).trigger('change');
	};
	dismissAddAnotherPopup.original = originalDismissAddAnotherPopup;
}

function showAddAnotherPopupReturningWindow(triggeringLink) {
    /* django's version doesn't give us the window object :( */
    var name = triggeringLink.id.replace(/^add_/, '');
    name = id_to_windowname(name);
    href = triggeringLink.href
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return win;
}

django.jQuery(document).ready(function() {
  
  var $ = $ || jQuery || django.jQuery,
  		relatedWidgetCSSSelector = '.related-widget-wrapper-change-link, .related-widget-wrapper-delete-link',
  		hrefTemplateAttr = 'data-href-template';
  
  $('.related-widget-wrapper').live('change', function(){
  	var siblings = $(this).nextAll(relatedWidgetCSSSelector);
  	if (!siblings.length) return;
  	if (this.value) {
  		var val = this.value;
  		siblings.each(function(){
  			var elm = $(this);
  			elm.attr('href', interpolate(elm.attr(hrefTemplateAttr), [val]));
  		});
  	} else siblings.removeAttr('href');
  });
	
	$('.related-widget-wrapper-link').live('click', function(){
		if (this.href) {
            var win = showAddAnotherPopupReturningWindow(this);
            win.dismissEditRelatedPopup = dismissEditRelatedPopup;
            win.edit_related_popup_done = false;
            $(win).unload(function() {
                win.edit_related_popup_done = true;
            }
        }
        return false;
	});
  
    if ( document.location.search == '?_popup=1' && edit_related_popup_done )
        dismissEditRelatedPopup(window, 1, 'asdf');
});
