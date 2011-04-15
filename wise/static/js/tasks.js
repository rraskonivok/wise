(function() {
  var ApplyRule, Message, websock;
  websock = require('connection').websock;
  Message = require('messages').Message;
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
    msg = new Message({
      task: 'rule',
      args: rule,
      operands: operands,
      nsi: NAMESPACE_INDEX
    });
    image = [];
    if (websock.isConnected()) {
      return websock.send(msg);
    }
  };
  window.apply_rule = ApplyRule;
}).call(this);
