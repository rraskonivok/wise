module 'connection', (exports) ->

    ###
    Websocket Connection
    Wraps socket.io 
    ###
    class Connection

        connect_socket: ->
            socket = new io.Socket(
                WEBSOCKET_HOST
                port: WEBSOCKET_PORT
                transports: [
                     'websocket'
                     'flashsocket'
                     'htmlfile'
                     'xhr-multipart'
                     'xhr-polling'
                     'jsonp-polling']
            )

            socket.connect()
            @socket = socket


    exports.Connection = Connection
