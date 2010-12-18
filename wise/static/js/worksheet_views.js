_.templateSettings = {
  interpolate: /\{\{(.+?)\}\}/g
};

//TODO: Experiment with this somemore
//$(window).scroll(function () {
//    var a=$("#sidebar"),b=a.offset().top;
//    var d = a.css("position") == "fixed",
//        c = $(window).scrollTop() > b;
//    if (!d && c) a.css("top", "20px").css("position", "fixed");
//    else d && !c && a.css("top", "").css("left", "").css("position", "")
//});

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
        label: '>', 
        sexp: '(Gt (Placeholder ) (Placeholder ))',
    },

    {
        label: '<', 
        sexp: '(Lt (Placeholder ) (Placeholder ))',
    },
]

var InsertionToolbar = Backbone.View.extend({
   tagName: 'div',

   //Reference to the cell, where objects are appended
   model: null,

   initialize: function() {
       _.bindAll(this, 'new_type');
   },

   render: function() {
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

      this.$('.insertion_toolbar').html(
          this.insertion_menu.el
      );
  },

  events: {
    "click .node-outline": "collapse",
    "click .hide": "toggleAssums",
    "click .add": "insertion_menu",
    "click .del": "destroy",
    "click .save": "saveCell",
  },


  insertion_menu: function() {
      this.insertion_menu.toggle();
  },

  render: function () {
    $(this.el).append(this.menu());
    $(this.el).append(this.equations());
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

  collapse: function() {
    this.$('.equations').toggle(); 
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

// Cell selection buttons which appear in the top of the
// workspace 
var CellSelection = Backbone.View.extend({

  tagName: "a",

  className: 'active',

  events: {
    "mousedown": "toggle_visible",
  },

  initialize: function () {
    _.bindAll(this, 'render', 'make', 'handle_active');
    this.model.bind('change:active', this.handle_active);
  },

  render: function () {
    $(this.el).html(this.model.cid);
    $(this.el).bind("contextmenu", function (e) {
      return false;
    });
    return this;
  },

  toggle_visible: function (e) {
    //Right click - Toggle visibility of the cell
    if (e.button == 2) {
      this.model.dom().toggle();
      //        $(this.el).toggleClass('active');
      e.preventDefault();
      return false;
      //Left click - Select cell
    } else {
      activate_cell(this.model);
      //       this.model.dom().toggleClass('active');
    }
  },

  handle_active: function (cell, is_active) {
    active_cell = cell;
    if (is_active) {
      // Acts on the CellView object of the model
      this.model.view.set_active(true);
    } else {
      this.model.view.set_active(false);
    }
  }

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
    //        e.stopPropagation();
  },

});

// Selection Bar buttons for selection of Nodes
var NodeSelectionView = Backbone.View.extend({

  tagName: "button",

  className: "nodeselectbutton",

  events: {
    "click .ui-icon-circle-close": "unselectNode",
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
    if (val == false) {
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
