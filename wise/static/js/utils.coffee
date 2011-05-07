module 'utils', (exports) ->

    createUUID = ->
        s = []
        hexDigits = "0123456789abcdef"
        for i in [1..32]
            s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1)

        s[12] = "4"
        s[16] = hexDigits.substr((s[16] & 0x3) | 0x8, 1)

        uuid = s.join("")
        return uuid

    exports.createUUID = createUUID
