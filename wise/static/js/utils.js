(function() {
  module('utils', function(exports) {
    var createUUID;
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
    return exports.createUUID = createUUID;
  });
}).call(this);
