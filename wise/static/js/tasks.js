(function() {
  var ApplyRule, Connection, Task, websock, _ref;
  _ref = require('connection'), websock = _ref.websock, Connection = _ref.Connection;
  Task = require('messages').Task;
  ApplyRule = function(rule, operands, callback) {
    var image, msg, _operands;
    if (!operands) {
      if (Wise.Selection.isEmpty()) {
        return;
      }
      operands = Wise.Selection.sexps();
      _operands = Wise.Selection.toArray();
    } else {
      _operands = _.map(operands, function(obj) {
        if (obj.constructor === String) {
          return obj;
        } else {
          return obj.sexp();
        }
      });
    }
    msg = new Task({
      task: 'rule',
      args: rule,
      operands: operands,
      nsi: NAMESPACE_INDEX,
      uid: createUUID()
    });
    image = [];
    return websock.send(msg);
  };
  window.apply_rule = ApplyRule;
}).call(this);
