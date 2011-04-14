/*
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
*/

///////////////////////////////////////////////////////////
// Initalization
///////////////////////////////////////////////////////////

$(document).ajaxError(function (e, xhr, settings, exception) {
    Notifications.raise('AJAX_FAIL');
    var content = xhr.responseText;

    // Disable math operations until we restablish a connection
    //Wise.Settings.set({DISABLE_MATH: true});
    Wise.Log.serverError('Operation failed, since server did not respond',content);
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

if(!window.console) {
    window.console = {
        log : window.log
    };
}

// Begin Debugging Stuff
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
  Wise.Settings.set({DISABLE_MATH: false});
}

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds) {
      break;
    }
  }
}

// End Debugging Stuff
//----------------------

//Some JQuery Extensions
//----------------------

// Disable any animations on the worksheet
jQuery.fx.off = false;

$.fn.exists = function () {
  return $(this).length > 0;
}

$.fn.replace = function (htmlstr) {
  return $(this).replaceWith(htmlstr);
};

$.fn.id = function () {
  return $(this).attr('id');
};

$.fn.cid = function () {
  return $(this).attr('id');
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

///////////////////////////////////////////////////////////
// Term Lookup Table
///////////////////////////////////////////////////////////

// Takes the inital JSON that Django injects into the page in the
// variable JSON_TREE and calls build_tree_from_json to initialize
// the term database
function init_nodes() {
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

function graft(preimage, json, html) {
    // Is the image a toplevel element (i.e. Equation )
    var is_toplevel = (json[0].toplevel);
    nsym = preimage.view.el.replace(html);
    var newnode = null;

    if (is_toplevel) {
      newnode = graft_toplevel_from_json(
          // Graft on top of the old node
          Wise.Nodes.getByCid(preimage.cid),
          // Build the new node from the response JSON
          json
      );

    } else {
      newnode = graft_fragment_from_json(
          // Graft on top of the old node
          Wise.Nodes.getByCid(preimage.cid),
          // Build the new node from the response JSON
          json
      );
    }

    return newnode;
}

// Heartbeat to check to see whether the server is alive
function heartbeat() {
  $.ajax({
    url: '/hb',
    dataType: 'html',
    type: 'GET',
    success: function () {
      notify("Server is up.");
    },
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
      //$('#selectionlist').effect("highlight", {
        //color: '#E6867A'
      //}, 500);

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

  $.ajax({
    type: 'POST',
    url: "/cmds/apply_rule/",
    data: data,
    datatype: 'json',
    success: function (response) {
        if (response.error) {
          Wise.Log.error(response.error);
          return;
        }

        if (!response) {
          error('Server did not repsond to request.');
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
          var image_json = response.new_json[i];
          var image_html = response.new_html[i];

          switch(image_html) {
              case 'pass':
                  break;
              case 'delete':
                  preimage.remove();
                  break;
              case undefined:
                  preimage.remove();
                  break;
              default:
                  newnode = graft(preimage, image_json, image_html);
                  Wise.last_expr = newnode.root;
                  Wise.Selection.clear();

                  if(callback) {
                    callback(image);
                  }
          }

        }

    }
  });

}

function use_infix(code) {
  // Sends raw (with proper security restrictions) Pure code 
  // to the server and attempts to create new nodes from the 
  // result
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

  var operands = Wise.Selection.toArray();

  var postdata = {};
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
        Wise.CmdLine.error(response.error);
        return;

      } else {
        Wise.CmdLine.hide();
        Wise.CmdLine.hideError();
      }

      if(!response.namespace_index) {
          Wise.Log.error('Null namespace index');
          return;
      }

      NAMESPACE_INDEX = response.namespace_index;

      for (var i = 0; i < response.new_html.length; i++) {
        var preimage = operands[i];
        var image_json = response.new_json[i];
        var image_html = response.new_html[i];

        switch(image_html) {
            case 'pass':
                break;
            case 'delete':
                preimage.remove();
                break;
            case undefined:
                preimage.remove();
                break;
            default:
                newnode = graft(preimage, image_json, image_html);
                Wise.last_expr = newnode.root;
                Wise.Selection.clear();
        }
      }
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
          var image_json = response.new_json[i];
          var image_html = response.new_html[i];

          switch(image_html) {
              case 'pass':
                  break;
              case 'delete':
                  preimage.remove();
                  break;
              case undefined:
                  preimage.remove();
                  break;
              default:
                  newnode = graft(preimage, image_json, image_html);
                  Wise.last_expr = newnode.root;
                  Wise.Selection.clear();

                  //if(callback) {
                    //callback(image);
                  //}
          }

        }

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

  $.ajax({
    type: 'POST',
    url: "/cmds/new_line/",
    data: data,
    datatype: 'json',
    success: function (data) {

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
    }

  });
}

function new_cell() {
  data = {};
  data.namespace_index = NAMESPACE_INDEX;
  data.cell_index = CELL_INDEX;

  $.ajax({
    type: 'POST',
    url: "/cmds/new_cell/",
    data: data,
    datatype: 'json',
    success: function (response) {

        if (response.error) {
          Wise.Log.error(response.error);
          return;
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

          Wise.last_cell = cell;

        }

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
// Palette Loading
///////////////////////////////////////////////////////////

function load_rules_palette() {
  $.ajax({
    url: '/rule_request/',
    dataType: "html",
    success: function (data) {
      $("#rules").replaceWith(data);

      $(".panel_category", "#rules_palette").bind('click', function () {
        $(this).next().toggle();
        return false;
      }).next().hide();

      //$('#rulesearch').keyup(function () {
          //var query = $("#rulesearch").val();
          //if (!query) {
              //$('#rulelist *').show();
          //} else {
              //$('#rulelist *').not(":contains('" + query + "')").hide();
          //}
      //});

      $('#searchform').submit(function () {
          var query = $("#rulesearch").val();
          if (!query) {
              $('#rulelist *').show();
          } else {
              $('#rulelist *').show();
              $('#rulelist *').not(":contains('" + query + "')").hide();
          }
          return false;
      });

		$(".panel_frame","#rulelist").sortable({
            scroll: false,
			connectWith: '#quickbar',
			forcePlaceholderSize: true,
			helper: function(e,li) {
				copyHelper= li.clone().insertAfter(li);
                // Append to the body to let it pass between
                // jquery layout panels
                return $(li).clone().appendTo('body').show();
			},
			stop: function() {
				copyHelper && copyHelper.remove();
			}
		}).disableSelection();

		$("#quickbar").sortable({
            scroll: false,
			receive: function(e,ui) {
                $("#quickbar span").unbind();
                $("#quickbar span").attr('title','');
				copyHelper= null;
			}
		}).disableSelection();

    }
  });
}

function load_math_palette() {
  $.ajax({
    url: '/palette/',
    dataType: "html",
    success: function (data) {

      $("#math_palette").replaceWith(data);

      //Make the palette sections collapsable
      $(".panel_category", "#math_palette").bind('click', function () {
        $(this).next().toggle();
        $(this).next().addClass("expanded");
        return false;
      }).next().hide();

      $('.uniform_button',"#math_palette").addClass("vtip");

      var width = "150";
      var xOffset = -10 - width; // x distance from mouse
      var yOffset = 10; // y distance from mouse

      // Add math font preload
      $(".vtip").unbind().hover(
          function(e) {
              this.t = this.title;
              this.title = '';
              this.top = (e.pageY + yOffset); this.left = (e.pageX + xOffset);

              $('body').append( '<p id="vtip">' + this.t + '</p>' );
              $('p#vtip').css({
                  "top":  this.top,
                  "left": this.left,
                  "width": 200
              }).fadeIn("slow");

          },
          function() {
              this.title = this.t;
              $("p#vtip").fadeOut("slow").remove();
          }
      ).mousemove(
          function(e) {
              this.top = (e.pageY + yOffset);
              this.left = (e.pageX + xOffset);

              $("p#vtip").css("top", this.top+"px").css("left", this.left+"px");
          }
      );

	$("td","#math_palette").sortable({
        scroll: false,
		connectWith: '#quickbar',
		forcePlaceholderSize: true,
		helper: function(e,li) {
			copyHelper= li.clone().insertAfter(li);
            // Append to the body to let it pass between
            // jquery layout panels
            return $(li).clone().appendTo('body').show();
		},
		stop: function() {
			copyHelper && copyHelper.remove();
		}
	});


    }
  });

}

///////////////////////////////////////////////////////////
// Command Line
///////////////////////////////////////////////////////////

function mkautocomplete() {
    $.getJSON('/dict/purelist',
        function(data) {
            // _compact in case null finds its way into 'data'
            keywords = _.compact(data);
            $("#cmdinput").autocomplete(keywords, {
                width: 320,
                max: 4,
                highlight: false,
                multiple: true,
                multipleSeparator: " ",
                scroll: true,
                scrollHeight: 300
            });
        }
    );
}

function makeEditor(o) {
    var editor = ace.edit(o);
    editor.setTheme("ace/theme/eclipse");
}

function rearrange() {
    // Specify global variable layout
    layout = $("#container").layout({ 
    applyDefaultStyles: true 

    ,   north__showOverflowOnHover: true

    ,   fxName: "none"
    ,	fxSpeed_open:			    750
    ,	fxSpeed_close:			    1500

	,	east__resizable:		    false
	,	east__spacing_open:	        20
	,	east__spacing_closed:	    20
    ,	east__slideTrigger_open:    "mouseover"
	,	east__size:				    300
	,	east__minSize:			    200
	,	east__maxSize:              Math.floor(screen.availWidth / 2)

	,	south__resizable:		    true
	,	south__slideable:		    false
	,	south__spacing_open:	    5
	,	south__spacing_closed:	    20
	,	south__minSize:			    50
	,	south__size:				50

	,	north__resizable:		    false
	,	north__slideable:		    false
	,	north__closable:		    false
	,	north__size:		        30

	,	west__minSize:			    100
    });
}
