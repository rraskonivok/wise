# Set up as a Backbone model so we can attach events to changes
# in state
Settings = new Backbone.Model

    DEBUG               : undefined
    DISABLE_TYPESETTING : false
    DISABLE_MATH        : false
    SERVER_HEARTBEAT    : false

Application = Backbone.Model.extend
    version: '0.1.3'

    # Created upon call of init()
    Worksheet    : null
    Nodes        : null
    Selection    : null
    Sidebar      : null
    Accelerators : null
    CmdLine      : null

    last_cell    : null
    last_expr    : null

    cmd_visible  : null
    # Debug flag is injected into the page via Django and mirros
    # the DEBUG flag set in settings.py
    debug        : undefined

Wise = new Application()
Wise.Settings = Settings
window.Wise = Wise
