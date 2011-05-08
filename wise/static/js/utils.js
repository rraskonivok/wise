(function() {
  module('utils', function(exports) {
    var createUUID, dialog;
    jQuery.fx.off = false;
    $.fn.exists = function() {
      return $(this).length > 0;
    };
    $.fn.replace = function(htmlstr) {
      return $(this).replaceWith(htmlstr);
    };
    $.fn.id = function() {
      return $(this).attr('id');
    };
    $.fn.cid = function() {
      return $(this).attr('id');
    };
    $.fn.disableTextSelect = function() {
      return this.each(function() {
        if ($.browser.mozilla) {
          return $(this).css('MozUserSelect', 'none');
        } else if ($.browser.msie) {
          return $(this).bind('selectstart', function() {
            return false;
          });
        } else {
          return $(this).mousedown(function() {
            return false;
          });
        }
      });
    };
    createUUID = function() {
      var hexDigits, i, s, uuid;
      s = [];
      hexDigits = "0123456789abcdef";
      for (i = 1; i <= 32; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
      }
      s[12] = "4";
      s[16] = hexDigits.substr((s[16] & 0x3) | 0x8, 1);
      uuid = s.join("");
      return uuid;
    };
    dialog = function(text) {
      $('#error_dialog').text(text);
      return $('#error_dialog').dialog({
        modal: true,
        dialogClass: 'alert'
      });
    };
    exports.showmath = function() {
      return Wise.Selection.at(0).sexp();
    };
    exports.shownode = function() {
      if (Wise.Selection.isEmpty()) {
        console.log('Select something idiot!');
      }
      return Wise.Selection.at(0);
    };
    exports.rebuild_node = function() {
      return Wise.Selection.at(0).msexp();
    };
    return exports.createUUID = createUUID;
  });
}).call(this);
