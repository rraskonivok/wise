Wise = Backbone.Model.extend({
    version: '0.1alpha',

    // Created upon call of init()
    Worksheet: null,
    Nodes: null,
    Selection: null,
    Sidebar: null,
    Log: null,

    active_cell: null,
    cmd_visible: null,

});

Wise.Settings = new Backbone.Model({

    DEBUG: true,
    DISABLE_TYPESETTING: false,
    DISABLE_MATH: false,
    SERVER_HEARTBEAT: false,

})
