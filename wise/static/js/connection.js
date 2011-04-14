(function() {
  module('connection', function(exports) {
    var Connection, WEBSOCKET_HOST, WEBSOCKET_PORT;
    WEBSOCKET_PORT = 8000;
    WEBSOCKET_HOST = 'localhost';
    /*
    Websocket Connection
    Wraps socket.io
    */
    Connection = (function() {
      function Connection(name) {
        this.name = name;
      }
      Connection.prototype.Message = function(task, args, operands, namespace_index) {
        return {
          task: 'transform',
          args: ['package', 'transform_name'],
          operands: [],
          namespace_index: 0
        };
      };
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
