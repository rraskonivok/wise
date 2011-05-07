{createUUID} = require 'utils'

module 'messages', (exports) ->

    Message = (data) ->
        task     : data.task     || error('missing task')
        args     : data.args     || error('mssing args')
        operands : data.operands || error('missing operands')
        nsi      : data.nsi      || error('missing namespace_index')

    Task = (data) ->
        task     : data.task     || error('missing task')
        args     : data.args     || error('mssing args')
        operands : data.operands || error('missing operands')
        nsi      : data.nsi      || error('missing namespace_index')
        uid      : createUUID()

    exports.Message = Message
    exports.Task = Task
