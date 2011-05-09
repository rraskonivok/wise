(function() {
  /*
   Wise
   Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.
  */  var Task;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  Task = require('messages').Task;
  module('connection', function(exports) {
    var Connection, _HeartbeatMsg;
    _HeartbeatMsg = new Task({
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
      Connection.prototype.inital_connect = false;
      Connection.prototype.initalalize = function() {
        return _.bindAll(this, 'onConnect', 'onDisconnect', 'disconnect');
      };
      function Connection() {
        this.isConnected = __bind(this.isConnected, this);;        var socket;
        socket = new io.Socket(document.location.hostname);
        socket.connect();
        this.socket = socket;
        this.socket.on('connect', function() {
          if (!this.inital_connect) {
            this.inital_connect = true;
            log.debug('Websocket Connected');
          } else {
            log.debug('Websocket Reconnected');
            notify.info('Connection Restablished.');
          }
          return Wise.WorksheetView.unblock();
        });
        this.socket.on('disconnect', function() {
          log.error('Websocket Disconnected');
          notify.error('Connection Lost');
          return Wise.WorksheetView.block();
        });
      }
      Connection.prototype.send = function(data) {
        return this.socket.send(JSON.stringify(data));
      };
      Connection.prototype.disconnect = function() {
        return this.socket.disconnect();
      };
      Connection.prototype.isConnected = function() {
        if (!this.socket) {
          return false;
        } else {
          return this.socket.connected;
        }
      };
      return Connection;
    })();
    return exports.Connection = Connection;
  });
}).call(this);
