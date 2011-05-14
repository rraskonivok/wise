/*
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
*/

// --------------------------
// Templates
// --------------------------
var button_template = "<button>$label</button>";

var toplevel_types = [{
	label: 'Equation',
	sexp: 'eq'
},

{
	label: 'Definition',
	sexp: 'def'
},

{
	label: 'Greater Than',
	sexp: '(Gt (Placeholder ) (Placeholder ) )'
},

{
	label: 'Less Than',
	sexp: '(Lt (Placeholder ) (Placeholder ) )'
},
]

String.prototype.score = function(abbreviation,offset) {
  offset = offset || 0 // TODO: I think this is unused... remove
 
  if(abbreviation.length == 0) return 0.9
  if(abbreviation.length > this.length) return 0.0

  for (var i = abbreviation.length; i > 0; i--) {
    var sub_abbreviation = abbreviation.substring(0,i)
    var index = this.indexOf(sub_abbreviation)


    if(index < 0) continue;
    if(index + abbreviation.length > this.length + offset) continue;

    var next_string       = this.substring(index+sub_abbreviation.length)
    var next_abbreviation = null

    if(i >= abbreviation.length)
      next_abbreviation = ''
    else
      next_abbreviation = abbreviation.substring(i)
 
    var remaining_score   = next_string.score(next_abbreviation,offset+index)
 
    if (remaining_score > 0) {
      var score = this.length-next_string.length;

      if(index != 0) {
        var j = 0;

        var c = this.charCodeAt(index-1)
        if(c==32 || c == 9) {
          for(var j=(index-2); j >= 0; j--) {
            c = this.charCodeAt(j)
            score -= ((c == 32 || c == 9) ? 1 : 0.15)
          }

          // XXX maybe not port this heuristic
          // 
          //          } else if ([[NSCharacterSet uppercaseLetterCharacterSet] characterIsMember:[self characterAtIndex:matchedRange.location]]) {
          //            for (j = matchedRange.location-1; j >= (int) searchRange.location; j--) {
          //              if ([[NSCharacterSet uppercaseLetterCharacterSet] characterIsMember:[self characterAtIndex:j]])
          //                score--;
          //              else
          //                score -= 0.15;
          //            }
        } else {
          score -= index
        }
      }
   
      score += remaining_score * next_string.length
      score /= this.length;
      return score
    }
  }
  return 0.0
}

// --------------------------
// Worksheet View
// --------------------------
var WorksheetView = Backbone.View.extend({

	initialize: function() {
		_.bindAll(this, 'block', 'unblock');
	},

	block: function(msg) {
		var message = msg || '<h1>Waiting for Connection...</h1>';

		$('#center', this.el.selector).block({
			message: message,
			css: {
				border: '3px solid #a00'
			}
		});
	},

	unblock: function() {
		$("#center", this.el.selector).unblock();
	}

});

// --------------------------
// Siebar View
// --------------------------
var SidebarView = Backbone.View.extend({

	events: {
		"click    .math"           : "toggleMath",
		"dblclick .math"           : "expandAllMath",
		"dblclick .rules"          : "expandAllRules",
        //"click    .uniform_button" : "buttonPress",
	},

	initialize: function() {
		this.toggleState = 0;
		_.bindAll(this, 'toggleMath', 'onDisableMath');
		Wise.Settings.bind('change:DISABLE_MATH', this.onDisableMath);
	},

    buttonPress: function() {
        notify.info('Button clicked');
    },

	onDisableMath: function(model, state) {
		// If the server is unavailble to perform operations then
		// disable related panels
		//this.$('.math').button({disabled: state});
		//this.$('.rules').button({disabled: state});
	},

	expandAllMath: function() {
        if (this.toggleState) {
            this.$('#math_palette .panel_frame').hide();
        } else {
            this.$('#math_palette .panel_frame').show();
        }
		this.toggleState ^= 1;
	},

	expandAllRules: function() {
        $("#rulesearch").val('');

        // Force jQuery.liveUpdate to update
        $("#rulesearch").trigger('keyup');

        if (this.toggleState) {
            this.$('#rules_palette .panel_frame').hide();
        } else {
            this.$('#rules_palette .panel_frame').show();
        }
		this.toggleState ^= 1;
	},

});

// --------------------------
// Cell Related Views
// --------------------------
var InsertionToolbar = Backbone.View.extend({
	tagName: 'div',

	//Reference to the cell, where objects are appended
	model: null,

	initialize: function() {
		_.bindAll(this, 'new_type');
	},

	render: function() {
		if (!HAS_BROWSER) {
			return;
		}

		for (var tt in toplevel_types) {
			tt = toplevel_types[tt];

			var button = $(button_template.t({
				label: tt.label,
			}));

			button.bind('click', async.apply(this.new_type, tt.sexp));

			$(this.el).hide();
			$(this.el).append(button);
		}

		//Make buttons pretty
		//this.$('button').parent().buttonset();
		return this;
	},

	new_type: function(type) {
		new_line(type, this.model);
		$(this.el).toggle();
	},

	toggle: function() {
		$(this.el).toggle();
	}

});

// Cell object as manifest in the Workspace, This can be 
// referenced from the Cell object as Cell.view
var CellView = Backbone.View.extend({

	tagName: 'div',

	className: 'cell',
	insetion_menu: null,

	initialize: function() {
		this.insertion_menu = new InsertionToolbar({
			model: this.model,
		}).render();

		if (HAS_BROWSER) {
			this.$('.insertion_toolbar').html(
			this.insertion_menu.el);
		}
	},

	events: {
		"contextmenu .node-outline": "collapse",
		"click .hide": "toggleAssums",
		"click .add": "insertion_menu",
		"click .del": "destroyCell",
		"click .save": "saveCell",
	},

	insertion_menu: function() {
		this.insertion_menu.toggle();
	},

	destroyCell: function() {
		this.model.deleteCell();
	},

	render: function() {
		if (!HAS_BROWSER) {
			return;
		}
		return this;
	},

	set_active: function(state) {
		// Toggle the css activity indicator on the cell
		$(this.el).toggleClass('active', state);
	},

	addExpression: function(expr_view) {
		this.$('.equations').append(expr_view);
	},

	addAssumption: function(expr_view) {
		this.$('.assumptions').append(expr_view);
	},

	add: function() {
		new_line('eq', this.model.cid);
	},

	collapse: function(e) {
		this.$('.equations').toggle();
		return false;
	},

	toggleAssums: function() {
		this.$('.assumptions').toggle();
	},

	toggleExpressions: function() {
		this.$('.equations').toggle();
	},

	saveCell: function() {
		this.model.saveCell();
	},

	destroy: function() {
		// Prompt the user before they potentially destroy the cell
		// and all its subexpressions
		// If the cell has a correspondance in the database
		// then destroy it
		if (this.model.isNew() === false) {
			this.model.destroy({
				success: notify.info('COMMIT_SUCCESS')
			});
		}
		$(this.el).remove();
	},

});

// --------------------------
// Node Related Views
// --------------------------
var NodeView = Backbone.View.extend({

	events: {
		"click": "onClick",
		"mouseover": "onHoverIn",
		"mouseout": "onHoverOut",
	},

	highlightEverything: false,

	initialize: function() {
		_.bindAll(this, 'render', 'make', 'onClick');
	},

	onClick: function(e) {
		// If the ctrl key is down the container selection mode
		// is enabled an 'leaf' nodes are ignored
		if (e.ctrlKey) {
			if (this.model.hasChildren()) {
				this.model.toggleSelect();
				e.stopPropagation();
			}
		} else {
			this.model.toggleSelect();
			e.stopPropagation();
		}
	},

	onHoverIn: function(e) {
		// If the ctrl key is down the container selection mode
		// is enabled an 'leaf' nodes are ignored
		if (e.ctrlKey && this.model.hasChildren()) {
			$(this.el).addClass('preselect');
			e.stopPropagation();
		}

		// If the alt key is down the term selection mode
		// is enabled an 'branch' nodes are ignored
		if (e.altKey && ! this.model.hasChildren()) {
			$(this.el).addClass('preselect');
			e.stopPropagation();
		}
	},

	onHoverOut: function(e) {
		$(this.el).removeClass('preselect');
		//e.stopPropagation();
	},

});

// Selection Bar buttons for selection of Nodes
var NodeSelectionView = Backbone.View.extend({

	tagName: "button",

	className: "nodeselectbutton",

	events: {
		"click": "unselectNode",
		"mouseover": "highlight",
		"mouseout": "unhighlight",
	},

	css3effect: false,
	highlighteffect: false,

	initialize: function() {
		_.bindAll(this, 'render', 'make', 'unselect');
		this.model.bind('change:selected', this.unselect);
		Wise.Selection.getByCid(this.model.cid).selectionview = this;
	},

	render: function() {
		if (!HAS_BROWSER) {
			return;
		}

		$(this.el).button({
			icons: {
				primary: "ui-icon-circle-close"
			},
			label: this.model.get('type'),
			text: true
		});
		$("#selectionlist").append(this.el);
		return this;
	},

	unselectNode: function() {
		this.model.unselect();
	},

	// If 'selected' is changed on the model then destory self
	unselect: function(e, val) {
		if (val === false) {
			this.remove();
		}
	},

});

// --------------------------
// Command Line Views
// --------------------------
var CmdLineView = Backbone.View.extend({
	events: {
		"submit": "evaluate",
	},

	visible: false,

	initialize: function() {
		_.bindAll(this, 'hide', 'show', 'evaluate');
	},

	error: function(errormsg) {
		$("#cmderrormsg").text(errormsg);
		$("#cmderror").fadeIn();
	},

	setValue: function(value) {
		$("#cmdinput").val(value);
	},

    keylisten: function(e) {
        console.log(e);
        return true;
    },

	evaluate: function(e) {
		var input = this.$('#cmdinput');

        if(!input.val()) {
            this.hide();
            return;
        }

		require('tasks').EvalCode(input.val());

		// keeps form from being submitted
		//return false;
        e.preventDefault();
	},

	hideError: function() {
		$("#cmderror").fadeOut();
	},

	hide: function() {
		$("#cmderror").hide();
        this.$('#cmdinput').blur();
        this.$('#cmdinput').val("");
		this.visible = 0;
		window.innerlayout.close('south');
	},

	show: function() {
		window.innerlayout.open('south');
        this.el.show();

        // This command depends on the fact that there is no fx
        // on showing the south pane, otherwise we get a nasty
        // race condition with the focus
		this.$('#cmdinput').focus();

		this.visible = 1;
	},

	toggleVisible: function() {
		this.visible = this.visible ^ 1;

		if (!this.visible) {
			this.hide();
		} else {
			this.show();
		}

	},

});

