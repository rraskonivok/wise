(function() {
  /*
   Wise
   Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.
  */  var Connection;
  Connection = require('connection').Connection;
  module('init', function(exports) {
    var init, init_autocomplete, init_components, init_keyboard_shortcuts, init_layout, init_logger, init_nodes, init_views, make_editor, progress, prompt, test_mathml;
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
            return init_components();
          },
          "Go Back": function() {
            return history.go(-1);
          }
        }
      });
    };
    init_layout = function() {
      window.layout = $("#container").layout({
        north__showOverflowOnHover: true,
        fxName: "none",
        fxSpeed_open: 1,
        fxSpeed_close: 1,
        east__resizable: false,
        east__slidable: false,
        east__spacing_open: 20,
        east__spacing_closed: 20,
        east__size: 300,
        east__minSize: 200,
        east__maxSize: Math.floor(screen.availWidth / 2),
        south__resizable: true,
        south__slidable: false,
        south__spacing_open: 20,
        south__spacing_closed: 20,
        south__minSize: 50,
        south__size: 50,
        north__resizable: false,
        north__slidable: false,
        north__closable: false,
        north__size: 30,
        west__minSize: 100
      });
      return window.innerlayout = $('#center').layout({
        fxName: "none",
        fxSpeed_open: 1,
        fxSpeed_close: 1,
        center__paneSelector: "#inner-center",
        south__paneSelector: "#inner-south",
        south__resizable: true,
        south__size: 60,
        south__minSize: 60,
        south__initClosed: true
      });
    };
    init_keyboard_shortcuts = function() {
      var accel_template, doc, key_template;
      doc = $(document);
      key_template = "<kbd>$kstr</kbd>";
      accel_template = "<dt>$label</dt><dd>$keys</dd>";
      if (!Wise.Accelerators) {
        return;
      }
      return Wise.Accelerators.each(function(shortcut) {
        var accel, key_strokes, keys, list_item;
        keys = shortcut.get('keys');
        doc.bind('keydown', shortcut.get('keys'), shortcut.get('action'));
        key_strokes = shortcut.get('keys').split('+');
        accel = _.map(key_strokes, function(kstr) {
          return key_template.t({
            kstr: kstr
          });
        });
        accel.join('+');
        list_item = accel_template.t({
          label: shortcut.get('name'),
          keys: accel
        });
        return $("#keys_palette .list").append(list_item);
      });
    };
    init_nodes = function() {
      var cell_json, new_cell, _i, _len, _results;
      Wise.Worksheet = new WorksheetModel();
      Wise.Selection = new NodeSelectionManager();
      Wise.Nodes = new Backbone.Collection();
      _results = [];
      for (_i = 0, _len = JSON_TREE.length; _i < _len; _i++) {
        cell_json = JSON_TREE[_i];
        new_cell = build_cell_from_json(cell_json);
        _results.push(Wise.Worksheet.add(new_cell));
      }
      return _results;
    };
    init_views = function() {
      Wise.Sidebar = new SidebarView({
        el: $("#worksheet_sidebar")
      });
      Wise.CmdLine = new CmdLineView({
        el: $("#cmd")
      });
      Wise.WorksheetView = new WorksheetView({
        el: "#worksheet"
      });
      $("#container").show();
      layout.resizeAll();
      init_autocomplete();
      return $("#worksheet").show();
    };
    init_autocomplete = function() {
      return $.getJSON('/dict/purelist', function(data) {
        var keywords;
        keywords = _.compact(data);
        return $("#cmdinput").autocomplete(keywords, {
          width: 320,
          max: 4,
          highlight: false,
          multiple: true,
          multipleSeparator: " ",
          scroll: true,
          scrollHeight: 300
        });
      });
    };
    make_editor = function(o) {
      var editor;
      editor = ace.edit(o);
      return editor.setTheme("ace/theme/eclipse");
    };
    init_components = function() {
      init_nodes();
      log.info("Created nodes.");
      init_keyboard_shortcuts();
      init_views();
      window.onbeforeunload = function(e) {
        e = e || window.event;
        if (Wise.Worksheet.hasChangesToCommit()) {
          if (e) {
            e.returnValue = "You have unsaved changes.";
          }
          return "You have unsaved changes.";
        }
      };
      new MenuController();
      Backbone.history.start();
      Wise.Socket = new Connection();
      return progress(100);
    };
    init_logger = function() {
      var log;
      if (!Wise.debug) {
        return log = {
          toggle: function() {
            return null;
          },
          move: function() {
            return null;
          },
          resize: function() {
            return null;
          },
          clear: function() {
            return null;
          },
          debug: function() {
            return null;
          },
          info: function() {
            return null;
          },
          warn: function() {
            return null;
          },
          error: function() {
            return null;
          },
          profile: function() {
            return null;
          }
        };
      }
    };
    init = function() {
      Wise.debug = window.DEBUG;
      init_logger();
      if (HAS_BROWSER) {
        init_layout();
        async.series([
          function(callback) {
            return load_math_palette(callback);
          }, function(callback) {
            return load_rules_palette(callback);
          }, function(callback) {
            return $("#worksheet_sidebar").tabs();
          }
        ]);
        if (test_mathml()) {
          return init_components();
        } else {
          if (!$.browser.mozilla) {
            return prompt();
          }
        }
      } else {
        return init_components();
      }
    };
    return exports.init = init;
  });
}).call(this);
