(function() {
  module('messages', function(exports) {
    var Message;
    Message = function(data) {
      return {
        task: data.task || error('missing task'),
        args: data.args || error('mssing args'),
        operands: data.operands || error('missing operands'),
        nsi: data.nsi || error('missing namespace_index')
      };
    };
    return exports.Message = Message;
  });
}).call(this);
