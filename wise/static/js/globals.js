(function() {
  var Application, Settings, Wise;
  Settings = new Backbone.Model({
    DEBUG: window.DEBUG,
    DISABLE_TYPESETTING: false,
    DISABLE_MATH: false,
    SERVER_HEARTBEAT: false
  });
  Application = Backbone.Model.extend({
    version: '0.1.3',
    Worksheet: null,
    Nodes: null,
    Selection: null,
    Sidebar: null,
    Accelerators: null,
    CmdLine: null,
    last_cell: null,
    last_expr: null,
    cmd_visible: null,
    debug: window.DEBUG
  });
  Wise = new Application();
  Wise.Settings = Settings;
  window.Wise = Wise;
}).call(this);
