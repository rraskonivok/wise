(function() {
  /*
   Wise
   Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.
  */  var Message;
  Message = require('messages').Message;
  module('connection', function(exports) {
    var Connection, _HeartbeatMsg;
    _HeartbeatMsg = new Message({
      task: 'heartbeat',
      args: [],
      operands: [],
      nsi: 1
    });
    /*
    Websocket Connection
    Wraps socket.io
    */
    Connection = (function() {
      function Connection() {
        var socket;
        socket = new io.Socket(document.location.hostname);
        socket.connect();
        this.socket = socket;
        this.socket.on('connect', function() {
          return log.debug('Websocket Connected');
        });
        this.socket.on('disconnect', function() {
          return log.error('Websocket Disconnected');
        });
      }
      Connection.prototype.send = function(data) {
        console.log('sent data');
        return this.socket.send(JSON.stringify(data));
      };
      Connection.prototype.listen = function(signal) {};
      Connection.prototype.isConnected = function() {
        if (!this.socket) {
          return false;
        } else {
          return this.socket.connected;
        }
      };
      return Connection;
    })();
    exports.Connection = Connection;
    return exports.websock = new Connection();
  });
}).call(this);
