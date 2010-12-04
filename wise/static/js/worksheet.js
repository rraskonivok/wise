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
  error("Error connecting to server");
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
window.log = function () {
  log.history = log.history || [];
  log.history.push(arguments);
  if (this.console) {
    console.log(Array.prototype.slice.call(arguments));
  }
};

// Begin Debuggin' Stuff

function showmath() {
  return selection.at(0).sexp();
}

function shownode() {
  if (selection.isEmpty()) {
    window.log('Select something idiot!');
  }
  return selection.at(0);
}

function rebuild_node() {
  //Shit went down, so rebuild the sexp
  //apply_transform('base/Rebuild',[selection.at(0)]);
  selection.at(0).msexp();
}

// Beat on the server

function stress_test() {
  while (true) {
    apply_rule('algebra_normal', ['( Addition (Variable x) (Addition (Variable x) (Variable x)))']);
    sleep(300);
    console.log('done');
  }
}

DISABLE_SIDEBAR = false;

// End Debuggin' Stuff
//----------------------

//Some JQuery Extensions
//----------------------
// Disable any animations on the worksheet
jQuery.fx.off = true;

//jQuery.fx.off = true;
$.fn.exists = function () {
  return $(this).length > 0;
}

$.fn.replace = function (htmlstr) {
  return $(this).replaceWith(htmlstr);
};

//TODO: This is here for compatability reasons, move to fn.cid
$.fn.id = function () {
  return $(this).attr('id')
};

$.fn.cid = function () {
  return $(this).attr('id')
};

// Extract the id of an object and lookup its node
$.fn.node = function () {
  var node = NODES.getByCid($(this).id())
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
  NODES = new Backbone.Collection();
  WORKSHEET = new Worksheet();

  _.each(JSON_TREE, function (cell_json) {
    var new_cell = build_cell_from_json(cell_json);
    WORKSHEET.add(new_cell);

    var cs = new CellSelection({
      model: new_cell,
    });
    cs.render();

    $('#cell_selection').append(cs.el);
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
  var zipped = _.zip(selection, pattern);
  return _.map(zipped, _.isEqual);
}

function activate_cell(cell) {
  // If there is a active cell make it inactive
  if (active_cell) {
    active_cell.set({
      active: false
    });
  }
  cell.set({
    active: true
  });
  active_cell = cell;
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
// Stretchy Operators
///////////////////////////////////////////////////////////
ap = [];

function resize_all() {
  _.each(ap, resize_parentheses);
}

function resize_parentheses(node) {
  // TODO: Eventually change this to use a 'stretchy' class so
  // that we can scale other outfix operators besides
  // parentheses
  if (!(node.view)) {
    return;
  }

  if (!_.include(ap, node)) {
    ap.push(node);
  }

  // This value is determined empirically, I really should write
  // something prettier but I have better things to do
  // with my time, MathJax does this much better, maybe imitate
  // their 'fenced' style
  var scaling_factor = 0.3;
  var min_scale = 7;

  var fontfamily = null;

  var scale = node.view.el.height() * scaling_factor;

  if (scale < min_scale) {
    scale = min_scale
  };
  fontfamily = 'MathJax_Size4';

  //if(scale < 10) {
  //    fontfamily = 'MathJax_Size1';
  //}
  //if(scale > 20) {
  //    fontfamily = 'MathJax_Size2';
  //}
  //if(scale > 30) {
  //    fontfamily = 'MathJax_Size3';
  //}
  //if(scale > 40) {
  //    fontfamily = 'MathJax_Size4';
  //}
  var ps = node.view.el.children('.pnths').
  css('font-size', scale).
  css('font-family', fontfamily);
}

///////////////////////////////////////////////////////////
// Server Queries
///////////////////////////////////////////////////////////
ajaxqueue = $.manageAjax.create('queue', {
  queue: false,
  preventDoubbleRequests: false,
  cacheResponse: true
});

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

function apply_rule(rule, operands) {
  var data = {};
  data.rule = rule;
  data.namespace_index = NAMESPACE_INDEX;

  // If nodes are not explicitely passed then use 
  // the workspace's current selection
  if (!operands) {

    if (selection.isEmpty()) {
      //error("Selection is empty.");
      $('#selectionlist').effect("highlight", {
        color: '#E6867A'
      }, 500);

      return;
    }
    //Fetch the sexps for each of the selections and pass it
    //as a JSON array
    data.operands = selection.sexps();
    operands = selection.toArray();

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
    //data.selections = _.invoke(operands,'sexp');
  }

  // Fade elements while we wait for the server's response
  //_.each(operands, function(elem) {
  //    elem.dom().fadeTo('fast',0.5); 
  //});
  var image = [];

  $.post("/cmds/apply_rule/", data, function (response) {
    if (!response) {
      error('Server did not repsond to request.');
      return;
    }

    if (response.error) {
      error(response.error);
      base_mode();
      return;
    }

    NAMESPACE_INDEX = response.namespace_index;


    //Iterate over the elements in the image of the
    //transformation, attempt to map them 1:1 with the
    //elements in the domain. Elements mapped to 'null'
    //are deleted.
    for (var i = 0; i < response.new_html.length; i++) {
      var preimage = operands[i];

      if (response.new_html[i] == null) {
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
        var is_toplevel = (response.new_json[i][0].toplevel)

        if (is_toplevel) {

          nsym = preimage.dom().replace(response.new_html[i]);

          // !!!!!!!!!!!!!!!!
          // Swap the nodes reference in its Cell so
          // the cell isn't reference something that
          // doesn't exist anymore
          // !!!!!!!!!!!!!!!!
          newnode = graft_toplevel_from_json(
          // Graft on top of the old node
          NODES.getByCid(preimage.cid),
          // Build the new node from the response JSON
          response.new_json[i],
          // Optionally tell the new node what is
          // was before and which transform created
          // it
          data.rule);

          image.push(newnode);

        } else {

          nsym = preimage.dom().replace(response.new_html[i]);

          newnode = graft_tree_from_json(
          // Graft on top of the old node
          NODES.getByCid(preimage.cid),
          // Build the new node from the response JSON
          response.new_json[i],
          // Optionally tell the new node what is
          // was before and which transform created
          // it 
          data.rule);

          image.push(newnode);

        }

        //Typeset any latex in the html the server just spit out
//        mathjax_typeset($(nsym));
        resize_parentheses(newnode);
      }
    }

  }, "json");

  return image;
}

function apply_def(def, selections) {
  var data = {};

  data.def = def.sexp()
  data.namespace_index = NAMESPACE_INDEX;

  if (selections == null) {

    //Fetch the math for each of the selections
    if (selection.count == 0) {
      //            error("Selection is empty.");
      $('#selectionlist').effect("highlight", {
        color: '#E6867A'
      }, 500);
      return;
    }

    data.selections = selection.list_attr('math');

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
          NODES.getByCid(obj.id()), data.new_json[i], 'apply_def');

        } else {

          graft_tree_from_json(
          NODES.getByCid(obj.id()), data.new_json[i], 'apply_def');

        }

        var nsym = obj.replace(data.new_html[i]);
 //       nsym.fadeIn('slow');
//        mathjax_typeset($(nsym));
      }
    }

    NAMESPACE_INDEX = data.namespace_index;

    base_mode();
    resize_all();
  }, "json");
}

function use_infix(code) {
  // Sends raw Pure code to the server and attempts to create
  // new nodes from the result, this function is *NOT* secure
  // since Pure can execute arbitrary shell commands
  if (selection.isEmpty()) {
    $('#selectionlist').effect("highlight", {
      color: '#E6867A'
    }, 500);
    return;
  }

  if (selection.at(0).get('toplevel')) {
    //        error('Cannot rewrite toplevel element');
    selection.at(0).errorFlash();
    return;
  }

  selections = selection.toArray();

  postdata = {};
  postdata.namespace_index = NAMESPACE_INDEX;
  postdata.code = code;

  ajaxqueue.add({
    type: 'POST',
    async: 'false',
    url: "/cmds/use_infix/",
    data: postdata,
    datatype: 'json',
    success: function (data) {

      if (data.error) {
        error(data.error);
        base_mode();
        return;
      }

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
      for (var i = 0; i < data.new_html.length; i++) {
        obj = selections[i];

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
          var is_toplevel = (data.new_json[i][0].toplevel);

          if (is_toplevel) {
            if (!obj.toplevel) {
              //error('Cannot replace toplevel node with non-toplevel node');
              obj.errorFlash();
              //return;
            }
            nsym = obj.dom().replace(data.new_html[i]);

            graft_tree_from_json(
            NODES.getByCid(obj.cid), data.new_json[i]);

          } else {
            nsym = obj.dom().replace(data.new_html[i]);

            graft_tree_from_json(
            NODES.getByCid(obj.cid), data.new_json[i]);

          }
          //Typeset any latex in the html the server just spit out
          mathjax_typeset($(nsym));
        }
      }

      NAMESPACE_INDEX = data.namespace_index;

      base_mode();
      resize_all();
    }
  });
}

function apply_transform(transform, operands) {
  var postdata = {};
  postdata.transform = transform;
  postdata.namespace_index = NAMESPACE_INDEX;

  //if(operands.length == 1) {
  //    selections[0].fadeOut();
  //}
  if (!operands) {
    //Fetch the math for each of the selections
    if (selection.isEmpty()) {
      error("No selection to apply transform to");
      return;
    }
    // Get the sexps of the selected nodes
    postdata.selections = selection.sexps();
  } else {
    //TODO: change data.selections -> data.operands
    postdata.selections = _.map(operands, function (obj) {
      if (obj.constructor == String) {
        return obj;
      } else {
        return obj.sexp();
      }
    });
  }

  ajaxqueue.add({
    type: 'POST',
    async: 'false',
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
        base_mode();
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

            graft_toplevel_from_json(
            NODES.getByCid(obj.cid), response.new_json[i], postdata.transform);

          } else {
            nsym = obj.dom().replace(response.new_html[i]);

            graft_tree_from_json(
            NODES.getByCid(obj.cid), response.new_json[i], postdata.transform);
          }

          mathjax_typeset($(nsym));
        }
      }

      NAMESPACE_INDEX = response.namespace_index;

      base_mode();
      resize_all();
    }
  });
}

function new_line(type, index) {
  var data = {};
  data.namespace_index = NAMESPACE_INDEX;
  data.cell_index = CELL_INDEX;
  data.type = type;

  if (index != undefined) {
    active_cell = WORKSHEET.getByCid(index);
  }

  if (!active_cell) {
    if (WORKSHEET.length == 1) {
      active_cell = WORKSHEET.at(0);
    } else {
      error("Select a cell to insert into");
      return;
    }
  }

  // If the cell new then commit it to the database before we
  // so that all foreign keys on expression objects will
  // resolve properly
  if (active_cell.isNew()) {
    active_cell.save();
  }

  $.post("/cmds/new_line/", data, function (data) {

    if (data.error) {
      error(data.error);
    }

    if (data.new_html) {
      new_expr_html = $(data.new_html);
      active_cell.view.addExpression(new_expr_html);

      // Initiale the new expression in the term db
      var eq = build_tree_from_json(data.new_json);

      eq.cell = active_cell;
      eq.set({
        cell: active_cell.id
      });
      active_cell.addExpression(eq);

      // Render the html of the new expression
      mathjax_typeset(new_expr_html);

    }

    NAMESPACE_INDEX = data.namespace_index;
  }, 'json')
}

function new_assum(type, index) {
  var data = {};
  data.namespace_index = NAMESPACE_INDEX;
  data.cell_index = CELL_INDEX;
  data.type = type;

  if (index != undefined) {
    active_cell = WORKSHEET.getByCid(index);
  }

  if (!active_cell) {
    if (WORKSHEET.length == 1) {
      active_cell = WORKSHEET.at(0);
    } else {
      error("Select a cell to insert into");
      return;
    }
  }

  // If the cell new then commit it to the database before we
  // so that all foreign keys on expression objects will
  // resolve properly
  if (active_cell.isNew()) {
    active_cell.save();
  }

  $.post("/cmds/new_line/", data, function (data) {

    if (data.error) {
      error(data.error);
    }

    if (data.new_html) {
      new_expr_html = $(data.new_html);
      active_cell.view.addAssumption(new_expr_html);

      // Initiale the new expression in the term db
      var expr = build_tree_from_json(data.new_json, AssumptionTree);

      expr.cell = active_cell;
      expr.set({
        cell: active_cell.id
      });
      active_cell.addAssumption(expr);

      // Render the html of the new expression
      mathjax_typeset(new_expr_html);

    }

    NAMESPACE_INDEX = data.namespace_index;
  }, 'json')
}

function new_cell() {
  data = {};
  data.namespace_index = NAMESPACE_INDEX;
  data.cell_index = CELL_INDEX;

  $.post("/cmds/new_cell/", data, function (response) {

    if (!response) {
      error("Server did not respond.");
    }

    if (response.error) {
      error(response.error);
    }

    if (response.new_html) {

      var cell = build_cell_from_json(response.new_json);
      active_cell = cell;

      WORKSHEET.add(cell);
      CELL_INDEX = response.cell_index;
      NAMESPACE_INDEX = response.namespace_index;

      // Make the cell workspace object
      var view = new CellView({
        model: cell,
        id: cell.cid,
      });
      view.render();
      cell.view = view;

      // Make the cell selction object
      var cs = new CellSelection({
        model: cell,
      });
      cs.render();

      $("#workspace").append(view.el);
      $('#cell_selection').append(cs.el);

      // Make the new cell active
      cell.set({
        active: true
      });
    }
  });
}

///////////////////////////////////////////////////////////
// Math Parsing & Generating
///////////////////////////////////////////////////////////

function check_container(object) {

  // This handles stupid expression checking that is too expensive 
  // to do via Ajax, ie removing infix sugar 
  _.each(object.children(':not(script)'), function () {
    var prev = $(this).prev();
    var cur = $(this);
    var next = $(this).next();
    var last = $(object).children(':last-child');
    var first = $(object).children(':first-child');
    var group = $(this).attr('group');
    if (group != "") {

      // -- Rules for handling parenthesis --
      //This forces left parenthesis over to the left
      if (cur.hasClass('term') && next.hasClass('pnths') && next.hasClass('left')) {
        cur.swap(next);
      }

      //This forces left parenthesis over to the left
      if (cur.hasClass('pnths') && next.hasClass('term') && cur.hasClass('right')) {
        cur.swap(next);
      }

      // -- Rules for cleaning up infix sugar --
      group_type = $('#' + group).attr('math-type');

      //  A + + B  --> A  + B
      if (cur.hasClass('infix') && next.hasClass('infix')) {
        cur.remove();
      }

      // A + - B  --> A - B
      if (cur.hasClass('infix') && next.attr('math-type') == 'Negate') {
        cur.remove();
      }

      //  ( + A  --> ( A
      if (cur.hasClass('pnths') && next.hasClass('infix')) {
        next.remove();
      }

      //  + ) --> )
      if (cur.hasClass('infix') && next.hasClass('pnths')) {
        cur.remove();
      }

      // + A + B --> A + B
      if (first.hasClass('infix')) {
        first.remove();
      }

      // A + B + --> A + B
      if (last.hasClass('infix')) {
        last.remove();
      }

    }
  });
}

function mathjax_typeset(element) {
  //Typeset a DOM element when passed, if no element is passed
  //then typeset the entire page
  //if(DISABLE_TYPESETTING) {
  //    return;
  //}
  //Refresh math for a specific element
  //if (element) {
  //  MathJax.Hub.Queue(["Typeset", MathJax.Hub, element[0]]);
  //  MathJax.Hub.Queue();
  //}
  ////Refresh math Globally, shouldn't be called too much because
  ////it bogs down the browser
  //else {
  //  console.log('Refreshing all math on the page');
  //  MathJax.Hub.Process();
  //}
}

///////////////////////////////////////////////////////////
// Palette Loading / Handeling
///////////////////////////////////////////////////////////

function load_rules_palette() {
  if (DISABLE_SIDEBAR) {
    return;
  }

  $.ajax({
    url: '/rule_request',
    success: function (data) {
      $("#rules_palette").replace(data);
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
    success: function (data) {
      $("#math_palette").replace(data)

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
      //            $('.uniform_button','#math_palette').button();
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
