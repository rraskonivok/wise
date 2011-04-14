(function() {
  module('base', function(exports) {
    exports.WEBSOCKET_PORT = 8000;
    exports.WEBSOCKET_HOST = 'localhost';
    return exports.CLIENT_ID = null;
  });
  /*
  Microtemplating via DOM extension
  'foo $0,$1'.t(['a',35]) = 'foo a 35'
  */
  String.prototype._tregex = /(\$\w+)/g;
  String.prototype.template = String.prototype.t = function() {
    var args;
    if (arguments[0] instanceof Array) {
      return arguments[0].map(this.t, this).join("");
    } else {
      args = typeof arguments[0] === "object" ? arguments[0] : arguments;
    }
    return this.replace(this._tregex, function(match) {
      return args[match.substr(1)];
    });
  };
  Element.prototype.template = Element.prototype.t = Element.prototype.template = function() {
    this._tcache = this._tcache || this.innerHTML;
    return this.innerHTML = this._tcache.t.apply(this._tcache, arguments);
  };
}).call(this);
