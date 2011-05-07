(function() {
  var createUUID;
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
