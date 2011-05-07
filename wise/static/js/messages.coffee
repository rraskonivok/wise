###
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
###

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
