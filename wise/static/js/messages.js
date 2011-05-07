(function() {
  /*
   Wise
   Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.
  */  var createUUID;
  createUUID = require('utils').createUUID;
  module('messages', function(exports) {
    var Message, Task;
    Message = function(data) {
      return {
        task: data.task || error('missing task'),
        args: data.args || error('mssing args'),
        operands: data.operands || error('missing operands'),
        nsi: data.nsi || error('missing namespace_index')
      };
    };
    Task = function(data) {
      return {
        task: data.task || error('missing task'),
        args: data.args || error('mssing args'),
        operands: data.operands || error('missing operands'),
        nsi: data.nsi || error('missing namespace_index'),
        uid: createUUID()
      };
    };
    exports.Message = Message;
    return exports.Task = Task;
  });
}).call(this);
