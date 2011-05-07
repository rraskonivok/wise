(function() {
  /*
   Wise
   Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.
  */  var ApplyRule, Connection, ResultCallback, ResultQueue, Task, websock, _ref;
  _ref = require('connection'), websock = _ref.websock, Connection = _ref.Connection;
  Task = require('messages').Task;
  ResultQueue = [];
  ResultCallback = {};
  window.ResultQueue = ResultQueue;
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
    websock.send(task);
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
  websock.socket.on('message', function(msg) {
    if (ResultQueue[0] === msg.uid) {
      console.log('processing task', msg.uid);
      ResultQueue.pop();
      return ResultCallback[msg.uid].call(null, JSON.parse(msg.result));
    }
  });
  window.apply_rule = ApplyRule;
}).call(this);
