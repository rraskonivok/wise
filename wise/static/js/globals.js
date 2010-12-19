Wise = Backbone.Model.extend({
    version: '0.1alpha',

    // Created upon call of init()
    Worksheet: null,
    Nodes: null,
    Selection: null,
    Sidebar: null,

    active_cell: null,
    cmd_visible: null,

});

Wise.Settings = {

    DISABLE_TYPESETTING: false,

}
