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

        constructor: ->
            socket = new io.Socket(document.location.hostname)
            socket.connect()

            @socket = socket

            #@socket.on 'message',(data) ->
            #    log.info('new message')
            #    console.log JSON.parse(data.result)

            @socket.on 'connect', () ->
                log.debug('Websocket Connected')

            @socket.on 'disconnect', () ->
                log.error('Websocket Disconnected')


        send: (data) ->
            console.log('sent data')
            @socket.send(JSON.stringify(data))

        listen: (signal) ->

        isConnected: ->
            if not @socket
                return false
            else
                return @socket.connected

    exports.Connection = Connection
    exports.websock = new Connection()
