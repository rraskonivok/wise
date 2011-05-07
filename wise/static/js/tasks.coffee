{websock, Connection} = require 'connection'
{Task} = require 'messages'

ResultQueue = []
ResultCallback = {}

window.ResultQueue = ResultQueue

ApplyRule = (rule, operands, callback) ->

    # If nodes are not explicitely passed then use
    # the workspace's current selection
    if not operands

        if Wise.Selection.isEmpty()
             return

        # Fetch the sexps for each of the selections and pass it
        # as a JSON array
        operands = Wise.Selection.sexps()
        _operands = Wise.Selection.toArray()

    else
        # Operands can a mix of Expression objects or literal string
        # sexp in either case we pass the sexp to the sever
        _operands = _.map operands, (obj) ->
            if (obj.constructor == String)
                return obj
            else
                return obj.sexp()

    task = new Task
        task     : 'rule'
        args     : rule
        operands : operands
        nsi      : NAMESPACE_INDEX


    image = []

    # The uid for this given task, used to track during all queing
    # processes
    uid = task.uid
    websock.send(task)

    ResultQueue.push(uid)
    ResultCallback[uid] = (result) ->
        result = JSON.parse(result)
        window.result = result
        len = result.new_html.length - 1
        window.NAMESPACE_INDEX = result.namespace_index
        console.log(window.NAMESPACE_INDEX, result.namespace_index)

        for i in [0..len]
            preimage   = _operands[i]
            image_json = result.new_json[i]
            image_html = result.new_html[i]

            switch image_html
                when 'delete' then preimage.remove()
                when undefined then preimage.remove()
                else
                    newnode = graft(preimage, image_json, image_html)
                    Wise.last_expr = newnode.root
                    Wise.Selection.clear()

websock.socket.on 'message', (msg) ->
    # If result is the at the top of the queue then just do
    # execute the callback and we're done
    if ResultQueue[0] == msg.uid
        console.log 'processing task', msg.uid
        ResultQueue.pop()
        ResultCallback[msg.uid].call(null, JSON.parse(msg.result))

window.apply_rule = ApplyRule
