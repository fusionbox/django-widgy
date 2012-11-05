(function(window, undefined) {
  // IE doesn't accept periods or dashes in the window name, but the element IDs
  // we use to generate popup window names may contain them, therefore we map them
  // to allowed characters in a reversible way so that we can locate the correct 
  // element when the popup window is dismissed.
  function id_to_windowname(text) {
      text = text.replace(/\./g, '__dot__');
      text = text.replace(/\-/g, '__dash__');
      return text;
  }

  function windowname_to_id(text) {
      text = text.replace(/__dot__/g, '.');
      text = text.replace(/__dash__/g, '-');
      return text;
  }

  function html_unescape(text) {
      // Unescape a string that was escaped using django.utils.html.escape.
      text = text.replace(/&lt;/g, '<');
      text = text.replace(/&gt;/g, '>');
      text = text.replace(/&quot;/g, '"');
      text = text.replace(/&#39;/g, "'");
      text = text.replace(/&amp;/g, '&');
      return text;
  }
    var SelectBox =  {
      cache: {},
      init: function(id) {
          var box = document.getElementById(id);
          var node;
          SelectBox.cache[id] = [];
          var cache = SelectBox.cache[id];
          for (var i = 0; (node = box.options[i]); i++) {
              cache.push({value: node.value, text: node.text, displayed: 1});
          }
      },
      redisplay: function(id) {
          // Repopulate HTML select box from cache
          var box = document.getElementById(id);
          box.options.length = 0; // clear all options
          for (var i = 0, j = SelectBox.cache[id].length; i < j; i++) {
              var node = SelectBox.cache[id][i];
              if (node.displayed) {
                  box.options[box.options.length] = new Option(node.text, node.value, false, false);
              }
          }
      },
      filter: function(id, text) {
          // Redisplay the HTML select box, displaying only the choices containing ALL
          // the words in text. (It's an AND search.)
          var tokens = text.toLowerCase().split(/\s+/);
          var node, token;
          for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
              node.displayed = 1;
              for (var j = 0; (token = tokens[j]); j++) {
                  if (node.text.toLowerCase().indexOf(token) == -1) {
                      node.displayed = 0;
                  }
              }
          }
          SelectBox.redisplay(id);
      },
      delete_from_cache: function(id, value) {
          var node, delete_index = null;
          for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
              if (node.value == value) {
                  delete_index = i;
                  break;
              }
          }
          var j = SelectBox.cache[id].length - 1;
          for (var i = delete_index; i < j; i++) {
              SelectBox.cache[id][i] = SelectBox.cache[id][i+1];
          }
          SelectBox.cache[id].length--;
      },
      add_to_cache: function(id, option) {
        console.log(id);
          SelectBox.cache[id].push({value: option.value, text: option.text, displayed: 1});
      },
      cache_contains: function(id, value) {
          // Check if an item is contained in the cache
          var node;
          for (var i = 0; (node = SelectBox.cache[id][i]); i++) {
              if (node.value == value) {
                  return true;
              }
          }
          return false;
      },
      move: function(from, to) {
          var from_box = document.getElementById(from);
          var to_box = document.getElementById(to);
          var option;
          for (var i = 0; (option = from_box.options[i]); i++) {
              if (option.selected && SelectBox.cache_contains(from, option.value)) {
                  SelectBox.add_to_cache(to, {value: option.value, text: option.text, displayed: 1});
                  SelectBox.delete_from_cache(from, option.value);
              }
          }
          SelectBox.redisplay(from);
          SelectBox.redisplay(to);
      },
      move_all: function(from, to) {
          var from_box = document.getElementById(from);
          var to_box = document.getElementById(to);
          var option;
          for (var i = 0; (option = from_box.options[i]); i++) {
              if (SelectBox.cache_contains(from, option.value)) {
                  SelectBox.add_to_cache(to, {value: option.value, text: option.text, displayed: 1});
                  SelectBox.delete_from_cache(from, option.value);
              }
          }
          SelectBox.redisplay(from);
          SelectBox.redisplay(to);
      },
      sort: function(id) {
          SelectBox.cache[id].sort( function(a, b) {
              a = a.text.toLowerCase();
              b = b.text.toLowerCase();
              try {
                  if (a > b) return 1;
                  if (a < b) return -1;
              }
              catch (e) {
                  // silently fail on IE 'unknown' exception
              }
              return 0;
          } );
      },
      select_all: function(id) {
          var box = document.getElementById(id);
          for (var i = 0; i < box.options.length; i++) {
              box.options[i].selected = 'selected';
          }
      }
    };

  var admin = {
    SelectBox: SelectBox,
    RelatedObjectLookups: {

    showAddAnotherPopup: function(triggeringLink) {
        var name = triggeringLink.id.replace(/^add_/, '');
        var href = triggeringLink.attributes.href.value;
        name = id_to_windowname(name);
        if (href.indexOf('?') == -1)
            href += '?_popup=1';
        else
            href  += '&_popup=1';
        var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
        win.focus();
        return false;
    },
    showRelatedObjectLookupPopup: function(triggeringLink) {
      var name = triggeringLink.id.replace(/^lookup_/, '');
      var href = triggeringLink.attributes.href.value;
      name = id_to_windowname(name);
      if (href.search(/\?/) >= 0)
          href += '&pop=1';
      else
          href += '?pop=1';
      var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
      win.focus();
      return false;
  },

    dismissRelatedLookupPopup: function(win, chosenId) {
      var name = windowname_to_id(win.name);
      var elem = document.getElementById(name);
      if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
          elem.value += ',' + chosenId;
      } else {
          document.getElementById(name).value = chosenId;
      }
      win.close();
    },

    dismissAddAnotherPopup: function(win, newId, newRepr) {
        // newId and newRepr are expected to have previously been escaped by
        // django.utils.html.escape.
        newId = html_unescape(newId);
        newRepr = html_unescape(newRepr);
        var name = windowname_to_id(win.name);
        var elem = document.getElementById(name);
        if (elem) {
            var elemName = elem.nodeName.toUpperCase();
            if (elemName == 'SELECT') {
                var o = new Option(newRepr, newId);
                elem.options[elem.options.length] = o;
                o.selected = true;
            } else if (elemName == 'INPUT') {
                if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
                    elem.value += ',' + newId;
                } else {
                    elem.value = newId;
                }
            }
        } else {
            var toId = name + "_to";
            elem = document.getElementById(toId);
            var o = new Option(newRepr, newId);
            SelectBox.add_to_cache(toId, o);
            SelectBox.redisplay(toId);
        }
        win.close();
      }
   }
};
  if ( typeof window.define === "function" && window.define.amd ) {
    window.define( "django_admin", [], function () { return admin; } );
  }
})(window);
