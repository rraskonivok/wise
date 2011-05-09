###
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
###

{Task} = require 'messages'

module 'connection', (exports) ->

    _HeartbeatMsg = new Task
        task     : 'heartbeat'
        args     : []
        operands : []
        nsi      : 1

    ###
    Websocket Connection
    Wraps socket.io
    ###
    class Connection

        inital_connect: false

        initalalize: ->
            _.bindAll(this, 'onConnect', 'onDisconnect')


        constructor: ->
            socket = new io.Socket(document.location.hostname)
            socket.connect()

            @socket = socket

            @socket.on 'connect', () ->
                if not @inital_connect
                    @inital_connect = true
                    log.debug('Websocket Connected')
                else
                    log.debug('Websocket Reconnected')
                Wise.WorksheetView.unblock()

            @socket.on 'disconnect', () ->
                log.error('Websocket Disconnected')
                Wise.WorksheetView.block()

        send: (data) ->
            console.log('sent data')
            @socket.send(JSON.stringify(data))

        isConnected: =>
            if not @socket
                return false
            else
                return @socket.connected

    exports.Connection = Connection
