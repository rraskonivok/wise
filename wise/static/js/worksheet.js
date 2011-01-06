/*
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

///////////////////////////////////////////////////////////
// Initalization
///////////////////////////////////////////////////////////
$(document).ajaxError(function () {
    Notifications.raise('AJAX_FAIL');

    // Disable math operations until we restablish a connection
    Wise.Settings.set({DISABLE_MATH: true});
    Wise.Log.warn('Operation failed, since server did not respond');
});

$(document).ready(function () {
  init();
});

$(document).ajaxStart(function () {
  $('#ajax_loading').show();
});

$(document).ajaxStop(function () {
  $('#ajax_loading').hide();
});

///////////////////////////////////////////////////////////
// Utilities
///////////////////////////////////////////////////////////
// Nerf the console.log function so that it doesn't accidently
// break if Firebug / JS Consle is turned off.
// Source: http://paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/

// Disable any animations on the worksheet
jQuery.fx.off = false;

window.log = function () {
  log.history = log.history || [];
  log.history.push(arguments);
  if (this.console) {
    console.log(Array.prototype.slice.call(arguments));
  }
};

if(!this.console) {
    this.console = {
        log : window.log
    };
}

// Begin Debuggin' Stuff
// ---------------------
function showmath() {
  return Wise.Selection.at(0).sexp();
}

function shownode() {
  if (Wise.Selection.isEmpty()) {
    window.log('Select something idiot!');
  }
  return Wise.Selection.at(0);
}

function rebuild_node() {
  //Shit went down, so rebuild the sexp
  Wise.Selection.at(0).msexp();
}

function server_up() {
  // The server is up available I assert it to be true
  Wise.Settings.set({DISABLE_MATH: false});

}

// Beat on the server
function stress_test() {
  while (true) {
    apply_rule('algebra_normal', ['( Addition (Variable x) (Addition (Variable x)\
                    (Variable x)))']);
    sleep(3000);
    console.log('done');
  }
}

DISABLE_SIDEBAR = false;

// End Debuggin' Stuff
//----------------------

//Some JQuery Extensions
//----------------------

$.fn.exists = function () {
  return $(this).length > 0;
}

$.fn.replace = function (htmlstr) {
  return $(this).replaceWith(htmlstr);
};

//TODO: This is here for compatability reasons, move to fn.cid
$.fn.id = function () {
  return $(this).attr('id');
};

$.fn.cid = function () {
  return $(this).attr('id');
};

// Extract the id of an object and lookup its node
$.fn.node = function () {
  var node = Wise.Nodes.getByCid($(this).id());
  if (!node) {
    error("The term you selected is 'broken', try refreshing its corresponding equation.");
    window.log($(this).id(), 'not initalized in term db.');
    return;
  }
  return node;
};

// Prevent selections from being dragged on the specifed elements
$.fn.disableTextSelect = function () {
  return this.each(function () {
    if ($.browser.mozilla) { //Firefox
      $(this).css('MozUserSelect', 'none');
    } else if ($.browser.msie) { //IE
      $(this).bind('selectstart', function () {
        return false;
      });
    } else { //Opera, etc.
      (this).mousedown(function () {
        return false;
      });
    }
  });
};

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds) {
      break;
    }
  }
}

///////////////////////////////////////////////////////////
// Initialize the Term DB
///////////////////////////////////////////////////////////
// Takes the inital JSON that Django injects into the page in the
// variable JSON_TREE and calls build_tree_from_json to initialize
// the term database

function init_nodes() {
//  Wise.Nodes = new Backbone.Collection();
//  Wise.Worksheet = new Worksheet();

//    Wise.Worksheet = Wise.worksheet;

    Wise.Worksheet = new WorksheetModel();
    Wise.Selection = new NodeSelectionManager();
    Wise.Nodes = new Backbone.Collection();

    _.each(JSON_TREE, function (cell_json) {
        var new_cell = build_cell_from_json(cell_json);
        Wise.Worksheet.add(new_cell);
    });
}

///////////////////////////////////////////////////////////
// Selection Handling
///////////////////////////////////////////////////////////

function selection_matches_pattern(pattern) {
  // [Equation, Addition] , [Equation, Multiplication]
  // _.isEqual(Equation, Equation) = true
  // _.isEqual(Addition, Multiplication) = false
  // _.all( [true, false] ) = false => does not match pattern
  //TODO add support for matching by toplevel or number of
  //children
  var zipped = _.zip(Wise.Selection, pattern);
  return _.map(zipped, _.isEqual);
}

///////////////////////////////////////////////////////////
// UI Handling
///////////////////////////////////////////////////////////

function ask(message, yescallback, nocallack) {
  $("#dialog-ask").dialog({
    closeOnEscape: true,
    modal: true,
    resizable: false,
    buttons: {
      Ok: yescallback,
    }
  });
}

function error(text) {
  $.pnotify({
    'Error': 'Regular Notice',
    pnotify_text: text,
    pnotify_delay: 5000
  });
}

function notify(text) {
  $.pnotify({
    '': 'Regular Notice',
    pnotify_text: text,
    pnotify_delay: 5000
  });
}

function dialog(text) {
  $('#error_dialog').text(text);
  $('#error_dialog').dialog({
    modal: true,
    dialogClass: 'alert'
  });
}

///////////////////////////////////////////////////////////
// Server Queries
///////////////////////////////////////////////////////////

// Heartbeat to check to see whether the server is alive
function heartbeat() {
  $.ajax({
    url: '/hb',
    dataType: 'html',
    type: 'GET',
    success: function (response) {},
    timeout: function () {
      error("Not responding");
    },
    error: function () {
      error("Not responding");
    },
  });
}

function apply_rule(rule, operands, callback) {
  var data = {};
  data.rule = rule;
  data.namespace_index = NAMESPACE_INDEX;

  // If nodes are not explicitely passed then use
  // the workspace's current selection
  if (!operands) {

    if (Wise.Selection.isEmpty()) {
      //error("Selection is empty.");
      $('#selectionlist').effect("highlight", {
        color: '#E6867A'
      }, 500);

      return;
    }
    //Fetch the sexps for each of the selections and pass it
    //as a JSON array
    data.operands = Wise.Selection.sexps();
    operands = Wise.Selection.toArray();

  } else {
    // Operands can a mix of Expression objects or literal string
    // sexp in either case we pass the sexp to the sever
    data.operands = _.map(operands, function (obj) {
      if (obj.constructor == String) {
        return obj;
      } else {
        return obj.sexp();
      }
    });
  }

  // Fade elements while we wait for the server's response
  //_.each(operands, function(elem) {
  //    elem.view.el.fadeTo('fast',0.5);
  //});
  var image = [];

  $.post("/cmds/apply_rule/", data, function (response) {
    if (!response) {
      error('Server did not repsond to request.');
      return;
    }

    if (response.error) {
      Wise.Log.error(response.error);
      return;
    }

    if(!response.namespace_index) {
        Wise.Log.error('Null namespace index');
        return;
    }

    NAMESPACE_INDEX = response.namespace_index;

    //Iterate over the elements in the image of the
    //transformation, attempt to map them 1:1 with the
    //elements in the domain. Elements mapped to 'null'
    //are deleted.
    for (var i = 0; i < response.new_html.length; i++) {
      var preimage = operands[i];

      if (response.new_html[i] === undefined) {
        //Desroy the preimage
        preimage.remove();
      }
      else if (response.new_html[i] == 'pass') {
        //Do nothing, map the preimage to itself
      }
      else if (response.new_html[i] == 'delete') {
        //Desroy the preimage
        preimage.remove();
      }
      else {
        // Is the image a toplevel element (i.e. Equation )
        var is_toplevel = (response.new_json[i][0].toplevel);

        if (is_toplevel) {

          nsym = preimage.view.el.replace(response.new_html[i]);

          // !!!!!!!!!!!!!!!!
          // Swap the nodes reference in its Cell so
          // the cell isn't reference something that
          // doesn't exist anymore
          // !!!!!!!!!!!!!!!!
          newnode = graft_toplevel_from_json(
              // Graft on top of the old node
              Wise.Nodes.getByCid(preimage.cid),

              // Build the new node from the response JSON
              response.new_json[i],

              // Optionally tell the new node what is
              // was before and which transform created
              // it
              data.rule
          );

          image.push(newnode);
          Wise.last_expr = newnode.root;

        }
        else {

          nsym = preimage.view.el.replace(response.new_html[i]);

          newnode = graft_fragment_from_json(
              // Graft on top of the old node
              Wise.Nodes.getByCid(preimage.cid),

              // Build the new node from the response JSON
              response.new_json[i],

              // Optionally tell the new node what is
              // was before and which transform created
              // it
              data.rule
          );

          image.push(newnode);
          Wise.last_expr = newnode.root;

        }

        if(callback) {
            callback(image);
        }
        Wise.Selection.clear();

      }
    }

  }, "json");
}

function apply_def(def, selections) {
  var data = {};

  data.def = def.sexp();
  data.namespace_index = NAMESPACE_INDEX;

  if (selections) {

    //Fetch the math for each of the selections
    if (Wise.Selection.count == 0) {
      //error("Selection is empty.");
      $('#selectionlist').effect("highlight", {
        color: '#E6867A'
      }, 500);
      return;
    }

    //TODO: This is vestigal
    data.selections = Wise.Selection.list_attr('math');

  }
  else {
    data.selections = _.invoke(selections, 'math');
  }

  window.log(data);

  $.post("/cmds/apply_def/", data, function (data) {

    if (data.error) {
      error(data.error);
      base_mode();
      return;
    }

    //Iterate over the elements in the image of the
    //transformation, attempt to map them 1:1 with the
    //elements in the domain. Elements mapped to 'null'
    //are deleted.
    for (var i = 0; i < data.new_html.length; i++) {
      obj = selections[i];

      obj.queue(function () {
        $(this).fadeTo('slow', 1);
        $(this).dequeue();
      });

      if (data.new_html[i] == null) {
        obj.remove();
      }
      else if (data.new_html[i] == 'pass') {
        //console.log("Doing nothing");
      }
      else if (data.new_html[i] == 'delete') {
        //console.log("Deleting - at some point in the future");
      }
      else {

        //changed this
        toplevel = (data.new_json[i][0].toplevel)

        if (toplevel) {
          build_tree_from_json(data.new_json[i])

          graft_tree_from_json(
          Wise.Nodes.getByCid(obj.id()), data.new_json[i], 'apply_def');

        } else {

          graft_tree_from_json(
          Wise.Nodes.getByCid(obj.id()), data.new_json[i], 'apply_def');

        }

        var nsym = obj.replace(data.new_html[i]);
      }
    }

    NAMESPACE_INDEX = data.namespace_index;

    base_mode();
  }, "json");
}

function use_infix(code) {
  // Sends raw Pure code to the server and attempts to create
  // new nodes from the result, this function is *NOT* secure
  // since Pure can execute arbitrary shell commands
  if (Wise.Selection.isEmpty()) {
    $('#selectionlist').effect("highlight", {
      color: '#E6867A'
    }, 500);
    return;
  }

  if (Wise.Selection.at(0).get('toplevel')) {
    //error('Cannot rewrite toplevel element');
    Wise.Selection.at(0).errorFlash();
    return;
  }

  selections = Wise.Selection.toArray();

  postdata = {};
  postdata.namespace_index = NAMESPACE_INDEX;
  postdata.code = code;

  $.ajax({
    type: 'POST',
    url: "/cmds/use_infix/",
    data: postdata,
    datatype: 'json',
    success: function (response) {
      if (!response) {
        error('Server did not repsond to request.');
        return;
      }

      if (response.error) {
        Wise.Log.error(response.error);
        return;
      }

      if(!response.namespace_index) {
          Wise.Log.error('Null namespace index');
          return;
      }
      NAMESPACE_INDEX = response.namespace_index;

      //if (!data.new_html) {
      //  error("Statement is not well-formed");
      //  $("#cmdinput").css('background-color', '#D4A5A5');
      //  return;
      //} else {
      //  hide_cmdline();
      //}

      //Iterate over the elements in the image of the
      //transformation, attempt to map them 1:1 with the
      //elements in the domain. Elements mapped to 'null'
      //are deleted.
      for (var i = 0; i < response.new_html.length; i++) {
        obj = selections[i];

        if (response.new_html[i] === null) {
          obj.remove();
        }
        else if (response.new_html[i] == 'pass') {
          //console.log("Doing nothing");
        }
        else if (response.new_html[i] == 'delete') {
          //console.log("Deleting - at some point in the future");
        }
        else {
          var is_toplevel = (response.new_json[i][0].toplevel);

          if (is_toplevel) {
            if (!obj.toplevel) {
              //error('Cannot replace toplevel node with non-toplevel node');
              obj.errorFlash();
              //return;
            }
            obj.view.el.replace(response.new_html[i]);

            var newtree = graft_tree_from_json(
                Wise.Nodes.getByCid(obj.cid), response.new_json[i]
            );

            Wise.last_expr = newtree.root;

          } else {
            nsym = obj.view.el.replace(response.new_html[i]);

            var newtree = graft_fragment_from_json(
                Wise.Nodes.getByCid(obj.cid), response.new_json[i]
            );

            Wise.last_expr = newtree.root;

          }
        }
      }

      Wise.Selection.clear();
    }
  });
}

function apply_transform(transform, operands) {
  var postdata = {};
  postdata.transform = transform;
  postdata.namespace_index = NAMESPACE_INDEX;

  if (!operands) {
    //Fetch the math for each of the selections
    if (Wise.Selection.isEmpty()) {
      error("No selection to apply transform to");
      return;
    }
    // Get the sexps of the selected nodes
    postdata.selections = Wise.Selection.sexps();
  }
  else {
    // Let the user pass mixed Node and String type objects to
    // maximize flexibility and map everything into some form of
    // sexp
    postdata.selections = _.map(operands, function (obj) {
      if (obj.constructor == String) {
        return obj;
      } else {
        return obj.sexp();
      }
    });
  }

  $.ajax({
    type: 'POST',
    url: "/cmds/apply_transform/",
    data: postdata,
    datatype: 'json',
    success: function (response) {

      if (!response) {
        error('Server side error in processing apply_transform.');
        return;
      }

      if (response.error) {
        error(response.error);
        return
      }

      //Iterate over the elements in the image of the
      //transformation, attempt to map them 1:1 with the
      //elements in the domain. Elements mapped to 'null'
      //are deleted.
      for (var i = 0; i < response.new_html.length; i++) {
        obj = operands[i];

        if (response.new_html[i] == null) {
          obj.remove();
        }
        else if (response.new_html[i] == 'pass') {
          //console.log("Doing nothing");
        }
        else if (response.new_html[i] == 'delete') {
          //console.log("Deleting - at some point in the future");
        }
        else {
          var is_toplevel = (response.new_json[i][0].toplevel);
          if (is_toplevel) {
            nsym = obj.dom().replace(response.new_html[i]);

            var newtree = graft_toplevel_from_json(
                Wise.Nodes.getByCid(obj.cid), response.new_json[i],
                postdata.transform
            );

            Wise.last_expr = newtree.root;

          } else {
            nsym = obj.dom().replace(response.new_html[i]);

            var newtree = graft_fragment_from_json(
                Wise.Nodes.getByCid(obj.cid), response.new_json[i],
                postdata.transform
            );

            Wise.last_expr = newtree.root;
          }
        }
      }
      NAMESPACE_INDEX = response.namespace_index;
    }
  });
}

function new_line(type, cell) {

  // If we aren't given an explicit cell and the number of cells
  // and there is not a single
  if(!cell) {

      if(Wise.Worksheet.length == 1) {
        cell = Wise.Worksheet.at(0);
      } else if ( Wise.last_cell ) {
        cell = Wise.last_cell;
      } else {
        error('Dont know where to insert');
        return;
      }
  }

  if(!type) {
    type = 'eq';
  }

  var data = {};
  data.namespace_index = NAMESPACE_INDEX;
  data.cell_index = CELL_INDEX;
  data.type = type;

  // If the cell new then commit it to the database before we
  // so that all foreign keys on expression objects will
  // resolve properly
  if (cell.isNew()) {
    cell.save();
  }

  $.post("/cmds/new_line/", data, function (data) {

    if (data.error) {
      Wise.Log.error(data.error);
    }

    if (data.new_html) {
      var new_expr_html = $(data.new_html);
      cell.view.addExpression(new_expr_html);

      // Initiale the new expression in the term db
      var eq = build_tree_from_json(data.new_json);

      eq.cell = cell;
      eq.set({
        cell: cell.id
      });
      cell.addExpression(eq);
    }

    NAMESPACE_INDEX = data.namespace_index;
  }, 'json')
}

//function new_assum(type, index) {
//  var data = {};
//  data.namespace_index = NAMESPACE_INDEX;
//  data.cell_index = CELL_INDEX;
//  data.type = type;
//
//  if (index != undefined) {
//    active_cell = Wise.Worksheet.getByCid(index);
//  }
//
//  if (!active_cell) {
//    if (Wise.Worksheet.length == 1) {
//      active_cell = Wise.Worksheet.at(0);
//    } else {
//      error("Select a cell to insert into");
//      return;
//    }
//  }
//
//  // If the cell new then commit it to the database before we
//  // so that all foreign keys on expression objects will
//  // resolve properly
//  if (active_cell.isNew()) {
//    active_cell.save();
//  }
//
//  $.post("/cmds/new_line/", data, function (data) {
//
//    if (data.error) {
//      error(data.error);
//    }
//
//    if (data.new_html) {
//      new_expr_html = $(data.new_html);
//      active_cell.view.addAssumption(new_expr_html);
//
//      // Initiale the new expression in the term db
//      var expr = build_tree_from_json(data.new_json, AssumptionTree);
//
//      expr.cell = active_cell;
//      expr.set({
//        cell: active_cell.id
//      });
//      active_cell.addAssumption(expr);
//
//    }
//
//    NAMESPACE_INDEX = data.namespace_index;
//  }, 'json')
//}

function new_cell() {
  data = {};
  data.namespace_index = NAMESPACE_INDEX;
  data.cell_index = CELL_INDEX;

  $.post("/cmds/new_cell/", data, function (response) {

    if (response.error) {
      Wise.Log.error(response.error);
    }

    if (response.new_html) {

      var cell = build_cell_from_json(response.new_json);
      Wise.last_cell = cell;

      Wise.Worksheet.add(cell);
      CELL_INDEX = response.cell_index;
      NAMESPACE_INDEX = response.namespace_index;

      $("#worksheet").append(response.new_html);

      console.log($("#"+cell.cid));

      // Make the cell workspace object
      var view = new CellView({
        el: $("#"+cell.cid),
        model: cell,
      });

      cell.view = view;

      // Make the cell selction object
      //var cs = new CellSelection({
      //  model: cell,
      //});

      //cs.render();

      Wise.last_cell = cell;

    }
  });
}

///////////////////////////////////////////////////////////
// Typesetting
///////////////////////////////////////////////////////////

//Typeset a DOM element when passed, if no element is passed
//then typeset the entire page
function mathjax_typeset(element) {
  if(Worksheet.Settings.get('DISABLE_TYPESETTING')) {
      return;
  }

  //Refresh math for a specific element
  if (element) {
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, element[0]]);
    MathJax.Hub.Queue();
  }
  //Refresh math Globally, shouldn't be called too much because
  //it bogs down the browser
  else {
    MathJax.Hub.Process();
  }
}

///////////////////////////////////////////////////////////
// Palette Loading / Handeling
///////////////////////////////////////////////////////////

function load_rules_palette() {
  if (DISABLE_SIDEBAR) {
    return;
  }

  $.ajax({
    url: '/rule_request/',
    dataType: "html", 
    success: function (data) {
      $("#rules_palette").replaceWith($(data));
      $("#rules_palette").hide();

      $(".panel_category", "#rules_palette").bind('click', function () {
        $(this).next().toggle();
        return false
      }).next().hide();

      // Ugliness to make Tooltips appear properly
      $('a[title]').qtip({
        style: {
          name: 'cream',
          tip: true
        },
        container: $('#rules_palette'),
        position: {
          corner: {
            target: 'topRight',
            tooltip: 'bottomLeft',
          },
          adjust: {
            x: 0,
            y: 0,
            screen: true,
          },
        },
      });
      // End Ugliness
    }
  });
}

function load_math_palette() {
  if (DISABLE_SIDEBAR) {
    return;
  }

  $.ajax({
    url: '/palette/',
    dataType: "html",
    success: function (data) {
      $("#math_palette").replaceWith($(data))

      //Make the palette sections collapsable
      $(".panel_category", "#math_palette").bind('click', function () {
        $(this).next().toggle();
        return false;
      }).next().hide();

      //Typeset the panel
      //MathJax.Hub.Typeset($(this).next()[0]);

      $("#math_palette").resizable({
        handles: 's'
      });

      $('#math_palette td').button();
    }
  });


}

///////////////////////////////////////////////////////////
// Command Line
///////////////////////////////////////////////////////////
$('#cmdline').submit(function () {
  use_infix($("#cmdinput").val());
  $("#cmdinput").blur();
  // Inject into scratchpad
  return false;
});
