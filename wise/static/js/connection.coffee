###
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
###

{Message} = require 'messages'

module 'connection', (exports) ->

    _HeartbeatMsg = new Message
        task     : 'heartbeat'
        args     : []
        operands : []
        nsi      : 1


    ###
    Websocket Connection
    Wraps socket.io
    ###
    class Connection

        heartbeat = Message

        constructor: ->
            socket = new io.Socket(document.location.hostname)
            socket.connect()

            @socket = socket

            @socket.on 'message',(data) ->
                alert('new message')
                #console.log JSON.parse(data.result)

        send: (data) ->
            console.log('sent data')
            @socket.send(JSON.stringify(data))

        listen: (signal) ->

        isConnected: ->
            if not @socket
                return false
            else
                return @socket.connected

        heartbeat: (trial) ->
            this.socket || error('not connected')
            trial = trial + 1000 || 1000

            #_heartbeat = ->
                #@socket.send(_HeartbeatMsg)
                #@socket.listen('heartbeat')
                #error 'try again in $0 seconds'.t(trials)
                #setTimeout(@heatbeat, trial)

    exports.Connection = Connection
    exports.websock = new Connection()
