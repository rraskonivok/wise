module 'connection', (exports) ->

    WEBSOCKET_PORT = 8000
    WEBSOCKET_HOST = 'localhost'

    ###
    Websocket Connection
    Wraps socket.io 
    ###
    class Connection

        constructor: (@name) ->

        Message: (task, args, operands, namespace_index) ->
            task            : 'transform'
            args            : ['package', 'transform_name']
            operands        : []
            namespace_index : 0

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
