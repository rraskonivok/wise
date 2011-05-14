(function() {
  var Task;
  Task = require('messages').Task;
  module('tasks', function(exports) {
    var ApplyRule, EvalCode, ResultFlush;
    window.ResultQueue_HWM = 5;
    window.ResultQueue = [];
    window.ResultCallback = {};
    ApplyRule = function(rule, operands, callback) {
      var image, task, uid, _operands;
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
      task = new Task({
        task: 'rule',
        args: rule,
        operands: operands,
        nsi: NAMESPACE_INDEX
      });
      image = [];
      uid = task.uid;
      log.profile(uid);
      Wise.Socket.send(task);
      ResultQueue.push(uid);
      return ResultCallback[uid] = function(result) {
        var i, image_html, image_json, len, newnode, preimage;
        result = JSON.parse(result);
        window.result = result;
        len = result.new_html.length - 1;
        window.NAMESPACE_INDEX = result.namespace_index;
        console.log(window.NAMESPACE_INDEX, result.namespace_index);
        for (i = 0; (0 <= len ? i <= len : i >= len); (0 <= len ? i += 1 : i -= 1)) {
          preimage = _operands[i];
          image_json = result.new_json[i];
          image_html = result.new_html[i];
          switch (image_html) {
            case 'delete':
              preimage.remove();
              break;
            case void 0:
              preimage.remove();
              break;
            default:
              newnode = graft(preimage, image_json, image_html);
              Wise.last_expr = newnode.root;
              Wise.Selection.clear();
          }
        }
        return log.profile(uid);
      };
    };
    EvalCode = function(code) {
      var image, operands, task, uid;
      if (Wise.Selection.isEmpty()) {
        $('#selectionlist').effect("highlight", {
          color: '#E6867A'
        }, 500);
        return;
      }
      if (Wise.Selection.at(0).get('toplevel')) {
        error('Cannot rewrite toplevel element');
        Wise.Selection.at(0).errorFlash();
        return;
      }
      operands = Wise.Selection.toArray();
      task = new Task({
        task: 'eval',
        args: code,
        operands: operands,
        nsi: NAMESPACE_INDEX
      });
      image = [];
      uid = task.uid;
      log.profile(uid);
      Wise.Socket.send(task);
      ResultQueue.push(uid);
      return ResultCallback[uid] = function(result) {
        var i, image_html, image_json, len, newnode, preimage;
        result = JSON.parse(result);
        window.result = result;
        console.log(result);
        if (result.error) {
          Wise.CmdLine.show();
          Wise.CmdLine.setValue(code);
          Wise.CmdLine.error(result.error);
          return;
        } else {
          Wise.CmdLine.hide();
          Wise.CmdLine.hideError();
        }
        window.result = result;
        len = result.new_html.length - 1;
        window.NAMESPACE_INDEX = result.namespace_index;
        for (i = 0; (0 <= len ? i <= len : i >= len); (0 <= len ? i += 1 : i -= 1)) {
          preimage = operands[i];
          image_json = result.new_json[i];
          image_html = result.new_html[i];
          switch (image_html) {
            case 'delete':
              preimage.remove();
              break;
            case void 0:
              preimage.remove();
              break;
            default:
              newnode = graft(preimage, image_json, image_html);
              Wise.last_expr = newnode.root;
              Wise.Selection.clear();
          }
        }
        return log.profile(uid);
      };
    };
    Wise.Socket.socket.on('message', function(msg) {
      if (ResultQueue[0] === msg.uid) {
        ResultQueue.pop();
        return ResultCallback[msg.uid].call(null, JSON.parse(msg.result));
      }
    });
    ResultFlush = function() {
      window.ResultQueue = [];
      return window.ResultCallback = {};
    };
    window.apply_rule = ApplyRule;
    window.use_infix = EvalCode;
    window.ResultFlush = ResultFlush;
    window.ResultQueue = ResultQueue;
    exports.ApplyRule = ApplyRule;
    return exports.EvalCode = EvalCode;
  });
}).call(this);
