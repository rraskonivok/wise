(function() {
  /*
   Wise
   Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.
  */  module('init', function(exports) {
    var init, init_components, init_keyboard_shortcuts, init_nodes, init_views, progress, prompt, test_mathml;
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
    init_keyboard_shortcuts = function() {
      var accel_template, doc, key_template;
      doc = $(document);
      key_template = _.template("<kbd>{{kstr}}</kbd>");
      accel_template = _.template("<dt>{{label}}</dt><dd>{{keys}}</dd>");
      if (!Wise.Accelerators) {
        return;
      }
      return Wise.Accelerators.each(function(shortcut) {
        var accel, key_strokes, keys, list_item;
        keys = shortcut.get('keys');
        doc.bind('keydown', shortcut.get('keys'), shortcut.get('action'));
        key_strokes = shortcut.get('keys').split('+');
        accel = _.map(key_strokes, function(kstr) {
          return key_template({
            kstr: kstr
          });
        });
        accel.join('+');
        list_item = accel_template({
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
      return $("#worksheet").show();
    };
    init_components = function() {
      init_nodes();
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
      new WorkspaceController();
      Backbone.history.start();
      return progress(100);
    };
    init = function() {
      var layout;
      load_math_palette();
      load_rules_palette();
      layout = rearrange();
      if (test_mathml()) {
        return init_components();
      } else {
        if (!$.browser.mozilla) {
          return prompt();
        }
      }
    };
    return exports.init = init;
  });
}).call(this);
