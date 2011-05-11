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
$(document).ajaxError(function(e, xhr, settings, exception) {
	notify.info('Request failed.');

	// Django stack trace, if DEBUG is enabled
	var content = xhr.responseText;
	dialog_html(content);

	// Disable math operations until we restablish a connection
	//Wise.Settings.set({DISABLE_MATH: true});
	log.error('AJAX request failed.');
});

function dialog_html(html_contents) {
	// Dump the Django stack trace given on a failed AJAX request out into a iframe
	$("#dialog").dialog({
		resizable: true
	});

	var $frame = $('<iframe style="width:200px; height:100px;"></iframe>');
	$('#dialog').html($frame);

	setTimeout(function() {
		var doc = $frame[0].contentWindow.document;
		var $body = $('body', doc);
		$body.html(html_contents);
		$("#dialog iframe").css('height', '100%');
		$("#dialog iframe").css('width', '100%');
	},
	500);

}

///////////////////////////////////////////////////////////
// Console
///////////////////////////////////////////////////////////
// Nerf the console.log function so that it doesn't accidently
// break if Firebug / JS Consle is turned off.
// Source: http://paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
//window.log = function () {
// log.history = log.history || [];
// log.history.push(arguments);
// if (this.console) {
//   console.log(Array.prototype.slice.call(arguments));
// }
//};
//
//if(!window.console) {
//   window.console = {
//       log : window.log
//   };
//}
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
		json);

	} else {
		newnode = graft_fragment_from_json(
		// Graft on top of the old node
		Wise.Nodes.getByCid(preimage.cid),
		// Build the new node from the response JSON
		json);
	}

	return newnode;
}

// Heartbeat to check to see whether the server is alive
function heartbeat() {
	$.ajax({
		url: '/hb',
		dataType: 'html',
		type: 'GET',
		success: function() {
			notify.info("Server is up.");
		},
		timeout: function() {
			notify.error("Not responding");
		},
		error: function() {
			notify.error("Not responding");
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
		postdata.selections = _.map(operands, function(obj) {
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
		success: function(response) {

			if (!response) {
				error('Server did not repsond to request.');
				return;
			}

			if (response.error) {
				Wise.Log.error(response.error);
				return;
			}

			if (!response.namespace_index) {
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

				switch (image_html) {
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
	if (!cell) {

		if (Wise.Worksheet.length == 1) {
			cell = Wise.Worksheet.at(0);
		} else if (Wise.last_cell) {
			cell = Wise.last_cell;
		} else {
			error('Dont know where to insert');
			return;
		}
	}

	if (!type) {
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
		success: function(data) {

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
		success: function(response) {

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

				console.log($("#" + cell.cid));

				// Make the cell workspace object
				var view = new CellView({
					el: $("#" + cell.cid),
					model: cell,
				});

				cell.view = view;

				Wise.last_cell = cell;

			}

		}
	});
}

///////////////////////////////////////////////////////////
// Palette Loading
///////////////////////////////////////////////////////////
function load_rules_palette() {
	$.ajax({
		url: '/rule_request/',
		dataType: "html",
		success: function(data) {
			$("#rules").replaceWith(data);

			$(".panel_category", "#rules_palette").bind('click', function() {
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
			$('#searchform').submit(function() {
				var query = $("#rulesearch").val();
				if (!query) {
					$('#rulelist *').show();
				} else {
					$('#rulelist *').show();
					$('#rulelist *').not(":contains('" + query + "')").hide();
				}
				return false;
			});

			$(".panel_frame", "#rulelist").sortable({
				scroll: false,
				connectWith: '#quickbar',
				forcePlaceholderSize: true,
				helper: function(e, li) {
					copyHelper = li.clone().insertAfter(li);
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
				receive: function(e, ui) {
					$("#quickbar span").unbind();
					$("#quickbar span").attr('title', '');
					copyHelper = null;
				}
			}).disableSelection();

		}
	});
}

function load_math_palette() {
	$.ajax({
		url: '/palette/',
		dataType: "html",
		success: function(data) {

			$("#math_palette").replaceWith(data);

			//Make the palette sections collapsable
			$(".panel_category", "#math_palette").bind('click', function() {
				$(this).next().toggle();
				$(this).next().addClass("expanded");
				return false;
			}).next().hide();

			$('.uniform_button', "#math_palette").addClass("vtip");

			var width = "150";
			var xOffset = - 10 - width; // x distance from mouse
			var yOffset = 10; // y distance from mouse
			// Add math font preload
			$(".vtip").unbind().hover(
			function(e) {
				this.t = this.title;
				this.title = '';
				this.top = (e.pageY + yOffset);
				this.left = (e.pageX + xOffset);

				$('body').append('<p id="vtip">' + this.t + '</p>');
				$('p#vtip').css({
					"top": this.top,
					"left": this.left,
					"width": 200
				}).fadeIn("slow");

			},
			function() {
				this.title = this.t;
				$("p#vtip").fadeOut("slow").remove();
			}).mousemove(
			function(e) {
				this.top = (e.pageY + yOffset);
				this.left = (e.pageX + xOffset);

				$("p#vtip").css("top", this.top + "px").css("left", this.left + "px");
			});

			$("td", "#math_palette").sortable({
				scroll: false,
				connectWith: '#quickbar',
				forcePlaceholderSize: true,
				helper: function(e, li) {
					copyHelper = li.clone().insertAfter(li);
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

