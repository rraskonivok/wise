module 'base', (exports) ->

    exports.WEBSOCKET_PORT = 8000
    exports.WEBSOCKET_HOST = 'localhost'
    exports.CLIENT_ID = null

    window.error = Notifications.raise

###
Microtemplating via DOM extension
'foo $0,$1'.t(['a',35]) = 'foo a 35'
###

String.prototype._tregex = /(\$\w+)/g
String.prototype.template = String.prototype.t = ->

	if arguments[0] instanceof Array
		return arguments[0].map(this.t, this).join("")

	else
        args = if typeof arguments[0] == "object" then arguments[0] else arguments
		return this.replace(this._tregex, (match) ->
            return args[match.substr(1)]
        )

Element.prototype.template = Element.prototype.t = Element.prototype.template = ->
    this._tcache = this._tcache || this.innerHTML
    this.innerHTML = this._tcache.t.apply(this._tcache, arguments)
