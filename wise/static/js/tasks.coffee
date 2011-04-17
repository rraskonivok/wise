{websock, Connection} = require 'connection'
{Message} = require 'messages'

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

    msg = new Message
        task     : 'rule'
        args     : rule
        operands : operands
        nsi      : NAMESPACE_INDEX


    image = []

    if websock.socket.connected
        websock.send(msg)
    else
        error 'Websocket dropped'
        websock = new Connection()
        ApplyRule(rule, operands, callback)

window.apply_rule = ApplyRule
