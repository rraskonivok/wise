module 'utils', (exports) ->

    # jQuery extensions
    jQuery.fx.off = false

    $.fn.exists = () ->
      return $(this).length > 0

    $.fn.replace = (htmlstr) ->
      return $(this).replaceWith(htmlstr)

    $.fn.id = () ->
      return $(this).attr('id')

    $.fn.cid = () ->
      return $(this).attr('id')


  # Prevent selections from being dragged on the specifed elements
    $.fn.disableTextSelect = () ->
      return this.each () ->

        if $.browser.mozilla
            $(this).css 'MozUserSelect', 'none'

        else if $.browser.msie
            $(this).bind 'selectstart', () ->
                return false
        else
            $(this).mousedown () ->
                return false

    createUUID = ->
        s = []
        hexDigits = "0123456789abcdef"
        for i in [1..32]
            s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1)

        s[12] = "4"
        s[16] = hexDigits.substr((s[16] & 0x3) | 0x8, 1)

        uuid = s.join("")
        return uuid


    dialog = (text) ->
        $('#error_dialog').text(text)
        $('#error_dialog').dialog
            modal: true
            dialogClass: 'alert'

    # -------------------
    # Debugging Utilities
    # -------------------

    exports.showmath = () ->
      return Wise.Selection.at(0).sexp()

    exports.shownode = () ->
        if Wise.Selection.isEmpty()
          console.log('Select something idiot!')
        return Wise.Selection.at(0)

    exports.rebuild_node = () ->
      # Rrebuild the sexp for the selected node
      Wise.Selection.at(0).msexp()

    exports.createUUID = createUUID
