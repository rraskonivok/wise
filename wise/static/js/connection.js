(function() {
  module('connection', function(exports) {
    /*
    Websocket Connection
    Wraps socket.io
    */    var Connection;
    Connection = (function() {
      function Connection() {}
      Connection.prototype.connect_socket = function() {
        var socket;
        socket = new io.Socket(WEBSOCKET_HOST, {
          port: WEBSOCKET_PORT,
          transports: ['websocket', 'flashsocket', 'htmlfile', 'xhr-multipart', 'xhr-polling', 'jsonp-polling']
        });
        socket.connect();
        return this.socket = socket;
      };
      return Connection;
    })();
    return exports.Connection = Connection;
  });
}).call(this);
