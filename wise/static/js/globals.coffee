Wise = Backbone.Model.extend
    version: '0.1.3'

        # Created upon call of init()
    Worksheet    : null
    Nodes        : null
    Selection    : null
    Sidebar      : null
    Accelerators : null
    CmdLine      : null
    Log          : null

    last_cell    : null
    last_expr    : null

    cmd_visible  : null

# Set up as a Backbone model so we can attach events to changes
# in state
Wise.Settings = new Backbone.Model

    DEBUG               : true
    DISABLE_TYPESETTING : false
    DISABLE_MATH        : false
    SERVER_HEARTBEAT    : false


window.Wise = Wise
