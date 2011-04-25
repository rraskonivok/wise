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

            @socket.on 'message',(msg) ->
                alert('new message')
                console.log msg

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
