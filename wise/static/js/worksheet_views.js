/*
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
*/


_.templateSettings = {
  interpolate: /\{\{(.+?)\}\}/g
};

var button_template = _.template("<button>{{label}}</button>");

var toplevel_types = [
    {
        label: 'Equation',
        sexp: 'eq',
    },

    {
        label: 'Definition',
        sexp: 'def',
    },

    {
        label: 'Greater Than',
        sexp: '(Gt (Placeholder ) (Placeholder ) )',
    },

    {
        label: 'Less Than',
        sexp: '(Lt (Placeholder ) (Placeholder ) )',
    },
]

function expand_trace(obj) {
    $('.trace:last',obj).css('position','fixed');
    $('.trace:last',obj).css('left','0');
    $('.trace:last',obj).css('bottom','0');
    $('.trace:last',obj).css('z-index','500');

    $('.trace:last iframe',obj).css('height',document.height/2);
    $('.trace:last iframe',obj).css('width',document.width);
}

function collapse_trace(obj) {
    $('.trace:last',obj).css('position','relative');
    $('.trace:last',obj).css('left','');
    $('.trace:last',obj).css('top','');
    $('.trace:last',obj).css('z-index','0');

    $('.trace:last iframe',obj).css('height','100%');
    $('.trace:last iframe',obj).css('width','100%');
}

var Logger = Backbone.Collection.extend({

    fatal: function(msg) {
        var err = {
            message: msg, 
            severity: 3,
            trace: null,
        };
        this.add(err);
    },

    error: function(msg) {
        var err = {
            message: msg, 
            severity: 2,
            trace: null,
        };
        this.add(err);
    },

    warn: function(msg) {
        var err = {
            message: msg, 
            severity: 1,
            trace: null,
        };
        this.add(err);
    },

    serverError: function(msg, trace) {
        var err = {
            message: msg, 
            severity: 1,
            trace: trace,
        };
        this.add(err);
    },

});

var LoggerView = Backbone.View.extend({

    events: {
      "click .expandtrace": "toggleTrace",
    },

    colors: ['yellow',      // Warnings
             'lightsalmon', // Errors
             'red'          // Fatal Errors
            ],

    colorstate: 0,
    activetrace: null,

    initialize: function() {
        _.bindAll(this, 'newError','makeStackTrace');
        this.model.bind('add',this.newError);
    },

    toggleTrace: function(e) {
        if(this.active_trace) {
            collapse_trace(this.active_trace);
            this.active_trace = null;
        }
        else {
            var obj = $(e.target).parent();
            expand_trace(obj);
            this.active_trace = obj;
        }
    },

    newError: function(err) {
        var error_template = _.template('<div class="errmsg">{{error}}<br/><span class="expandtrace">Expand</span>|<span class="collapsetrace">Collapse</span><div class="trace">{{trace}}</div></div>');

        var severity = err.get('severity');

        // Display the color indicator corresponding to the worst
        // active error
        if(severity >= this.colorstate) {
            var color = this.colors[err.get('severity')-1];
            $('#log_indicator').css('background-color', color); 
            this.colorstate = severity;
        }

        $('#log_indicator').effect('highlight');

        if(err.get('trace')) {
           this.makeStackTrace(err); 
           return;
        }

        this.$('.history').prepend(
            error_template({
                error: err.get('message'),
            })
        );
    },

    makeStackTrace: function(err) {
        var error_template = _.template('<div class="errmsg">{{error}}<br/><span class="expandtrace">Expand</span><div class="trace">{{trace}}</div></div><hr/>');
        error = error_template({
            error: err.get('message'),
            trace: '',
        })

        this.$('.history').prepend(
            error
        );

        var iframe = document.createElement("iframe");
        $('.trace:first','.history')[0].appendChild(iframe);

        var doc = iframe.document;
        if(iframe.contentDocument) {
            doc = iframe.contentDocument;
        } else if(iframe.contentWindow) {
            doc = iframe.contentWindow.document;
        }

        // Put the content in the iframe
        doc.open();
        doc.writeln(err.get('trace'));
        doc.close();

        var storeArea = doc.getElementById("storeArea");

    },

    resetState: function(err) {
        this.colorstate = 0;
        $('#log_indicator').css('background-color', ""); 
    },
});

var SidebarView = Backbone.View.extend({

  events: {
    "click .math": "toggleMath",
    "dblclick .math": "expandAllMath",

    "click .rules": "toggleRules",
    "click .settings": "toggleSettings",
    "click .terminal": "toggleTerminal",
    "click .keys": "toggleKeys",
  },

   initialize: function() {
        this.toggleState = 0;
       _.bindAll(this, 'toggleMath', 'onDisableMath');
        Wise.Settings.bind('change:DISABLE_MATH', this.onDisableMath); 
   },

   onDisableMath: function(model, state) {
        // If the server is unavailble to perform operations then
        // disable related panels
        //this.$('.math').button({disabled: state});
        //this.$('.rules').button({disabled: state});
   },

   expandAllMath: function() {
        if(this.toggleState) {
            this.$('#math_palette .panel_frame').hide();
        } else {
            this.$('#math_palette .panel_frame').show();
        }

        this.toggleState ^= 1;
   },

   toggleMath: function() {
        this.$('.palette').hide();
        this.$('#math_palette').show();
   },

   toggleRules: function() {
        this.$('.palette').hide();
        this.$('#rules_palette').show();
   },

   toggleSettings: function() {
        this.$('.palette').hide();
        this.$('#settings_palette').show();
   },

   toggleKeys: function() {
        this.$('.palette').hide();
        this.$('#keys_palette').show();
   },

   toggleTerminal: function() {
        this.$('.palette').hide();
        this.$('#terminal_palette').show();
        Wise.Log.view.resetState();
   },

});

var InsertionToolbar = Backbone.View.extend({
   tagName: 'div',

   //Reference to the cell, where objects are appended
   model: null,

   initialize: function() {
       _.bindAll(this, 'new_type');
   },

   render: function() {
        if(!HAS_BROWSER) {
            return;
        }

       for(var tt in toplevel_types) {
           tt = toplevel_types[tt];

           var button = $(button_template({
               label: tt.label,
           }));

           button.bind('click',
               async.apply(this.new_type, tt.sexp)
           );

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

  initialize: function () {
      this.insertion_menu = new InsertionToolbar({
          model: this.model,
      }).render();

      if(HAS_BROWSER) {
          this.$('.insertion_toolbar').html(
              this.insertion_menu.el
          );
      }
  },

  events: {
    "contextmenu .node-outline": "collapse",
    "click .hide" : "toggleAssums",
    "click .add"  : "insertion_menu",
    "click .del"  : "destroyCell",
    "click .save" : "saveCell",
  },

  insertion_menu: function() {
      this.insertion_menu.toggle();
  },

  destroyCell: function() {
      this.model.deleteCell();
  },

  render: function () {
    if(!HAS_BROWSER) {
        return;
    }
    return this;
  },

  set_active: function (state) {
    // Toggle the css activity indicator on the cell
    $(this.el).toggleClass('active', state);
  },


  addExpression: function (expr_view) {
    this.$('.equations').append(expr_view);
  },

  addAssumption: function (expr_view) {
    this.$('.assumptions').append(expr_view);
  },

  add: function () {
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

  saveCell: function () {
    this.model.saveCell();
  },

  destroy: function () {
    // Prompt the user before they potentially destroy the cell
    // and all its subexpressions
    // If the cell has a correspondance in the database
    // then destroy it
    if (this.model.isNew() == false) {
      this.model.destroy({
        success: Notifications.raise('COMMIT_SUCCESS'),
      });
    }
    $(this.el).remove();
  },

});

// Node Views as manifest as manipulative LaTeX in the worksheet
var NodeView = Backbone.View.extend({

  events: {
    "click": "onClick",
    "mouseover": "onHoverIn",
    "mouseout": "onHoverOut",
  },

  highlightEverything: false,

  initialize: function () {
    _.bindAll(this, 'render', 'make', 'onClick');
  },

  onClick: function (e) {
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

  onHoverIn: function (e) {
    // If the ctrl key is down the container selection mode
    // is enabled an 'leaf' nodes are ignored
    if (e.ctrlKey && this.model.hasChildren()) {
        $(this.el).addClass('preselect');
        e.stopPropagation();
    }

    // If the alt key is down the term selection mode
    // is enabled an 'branch' nodes are ignored
    if(e.altKey && !this.model.hasChildren()) {
        $(this.el).addClass('preselect');
        e.stopPropagation();
    }
  },

  onHoverOut: function (e) {
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

  initialize: function () {
    _.bindAll(this, 'render', 'make', 'unselect');
    this.model.bind('change:selected', this.unselect);
    Wise.Selection.getByCid(this.model.cid).selectionview = this;
  },

  render: function () {
    if(!HAS_BROWSER) {
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

  unselectNode: function () {
    this.model.unselect();
  },

  // If 'selected' is changed on the model then destory self
  unselect: function (e, val) {
    if (val === false) {
      this.remove();
    }
  },

  highlight: function (e) {
    //if (this.css3effect) {
    //  $('.MathJax_Display').addClass('modal');
    //  typsets = this.model.dom().find('.MathJax_Display');
    //  _.each(typsets, function (t) {
    //    $(t).removeClass('modal');
    //  });
    //  this.model.view.el.addClass('shadow');
    //  this.model.view.el.removeClass('selected');
    //} else if (this.highlighteffect) {
    //  this.model.view.el.addClass('highlight');
    //}
  },

  unhighlight: function (e) {
    //if (this.css3effect) {
    //  $('.MathJax_Display').removeClass('modal');
    //  this.model.view.el.removeClass('shadow');
    //} else if (this.highlighteffect) {
    //  this.model.view.el.removeClass('highlight');
    //}
  },

});

var CmdLineView = Backbone.View.extend({
    events: {
        "submit": "evaluate",
    },

    visible: false,

    initialize: function() {
        _.bindAll(this, 'hide','show');
    },

    error: function(errormsg) {
        $("#cmderrormsg").text(errormsg);
        $("#cmderror").fadeIn();
    },

    evaluate: function(e) {
        var input = this.$('#cmdinput');
        var success = use_infix( input.val() );

        if ( success ) {
            this.hide();
        }

        // keeps form from being submitted
        return false;
    },

    hideError: function() {
        $("#cmderror").fadeOut();
    },

    hide: function() {
        $("#cmderror").hide();
        this.el.hide();
        this.$('#cmdinput').blur();
        this.$('#cmdinput').val("");
        this.visible = 0;
    },

    show: function() {
        this.el.show();
        this.$('#cmdinput').focus();
        this.visible = 1;
    },

    toggleVisible: function() {
        this.visible = this.visible ^ 1;

        if(!this.visible) {
            this.hide();
        } else {
            this.show();
        }

    },

});
