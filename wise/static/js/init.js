(function() {
  module('init', function(exports) {
    var boot, init, progress, prompt, test_mathml;
    test_mathml = function() {
      var mml_namespace, test1, test2, test3;
      mml_namespace = "http://www.w3.org/1998/Math/MathML";
      test1 = document.createElementNS;
      test2 = document.createElementNS(mml_namespace, "mn");
      test3 = test2.isDefaultNamespace(document.namespaceURI);
      return !!test1 && !!test2 && !!test3;
    };
    progress = function(val) {
      $("#progressbar").progressbar({
        value: val
      });
      if (val >= 100) {
        return $("#progressbar").addClass('hidden');
      }
    };
    prompt = function() {
      $("#progressbar").removeClass('hidden');
      progress(10);
      $("#dialog").removeClass('hidden');
      return $("#dialog").dialog({
        resizable: false,
        height: 300,
        width: 350,
        modal: true,
        position: 'center',
        buttons: {
          "Proceed Anyways": function() {
            $(this).dialog("close");
            return boot();
          },
          "Go Back": function() {
            return history.go(-1);
          }
        }
      });
    };
    boot = function() {
      init_nodes();
      init_keyboard_shortcuts();
      Wise.Sidebar = new SidebarView({
        el: $("#worksheet_sidebar")
      });
      Wise.Log = new Logger();
      Wise.Log.view = new LoggerView({
        el: $('#terminal_palette'),
        model: Wise.Log
      });
      Wise.CmdLine = new CmdLineView({
        el: $("#cmd")
      });
      $("#container").show();
      mkautocomplete();
      $("#worksheet").show();
      window.onbeforeunload = function(e) {
        e = e || window.event;
        if (Wise.Worksheet.hasChangesToCommit()) {
          if (e) {
            e.returnValue = "You have unsaved changes.";
          }
          return "You have unsaved changes.";
        }
      };
      new WorkspaceController();
      Backbone.history.start();
      return progress(100);
    };
    init = function() {
      var layout;
      load_math_palette();
      progress(20);
      load_math_palette();
      progress(20);
      load_rules_palette();
      progress(30);
      layout = rearrange();
      if (test_mathml()) {
        return boot();
      } else {
        if (!$.browser.mozilla) {
          return prompt();
        }
      }
    };
    exports.test_mathml = test_mathml;
    return exports.init = init;
  });
}).call(this);
