(function() {
  var Wise;
  Wise = Backbone.Model.extend({
    version: '0.1.3',
    Worksheet: null,
    Nodes: null,
    Selection: null,
    Sidebar: null,
    Accelerators: null,
    CmdLine: null,
    Log: null,
    last_cell: null,
    last_expr: null,
    cmd_visible: null
  });
  Wise.Settings = new Backbone.Model({
    DEBUG: true,
    DISABLE_TYPESETTING: false,
    DISABLE_MATH: false,
    SERVER_HEARTBEAT: false
  });
  window.Wise = Wise;
}).call(this);
