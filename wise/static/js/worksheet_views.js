_.templateSettings = {
  interpolate : /\{\{(.+?)\}\}/g
};

var cell_menu = _.template('<div class="cellbuttons"><span class="add ui-icon ui-icon-circle-plus"></span><span class="del ui-icon ui-icon-circle-minus"></span><span class="save ui-icon ui-icon-disk"></span></div>')
var cell_template = _.template('<div id="{{id}}" class="cell"></div>');

// The view of the workspace Singleton
var WorksheetView = Backbone.View.extend({
    id: 'workspace',
});

// Cell object as manifest in the Workspace, This can be 
// referenced from the Cell object as Cell.view
var CellView = Backbone.View.extend({

  tagName: 'div',

  className: 'cell',

  initialize: function() {
      //this.model.bind('change', this.render);
  },

  events: {
    "click .add":   "add",
    "click .del":   "destroy",
    "click .save":  "save",
  },

  menu: cell_menu,

  render: function() {
      $(this.el).html(this.menu());
      return this;
  },

  set_active: function(state) {
      // Toggle the css activity indicator on the cell
      $(this.el).toggleClass('active',state);
  },


  addExpression: function(expr_view) {
      $(this.el).append(expr_view);    
  },

  add: function() {
      new_line('eq', this.model.cid);
  },
  
  save: function() {
    this.model.save({
        success: Notifications.raise('COMMIT_SUCCESS'),
    });
    this.model.saveExpressions();
  },

  destroy: function() {
    // Prompt the user before they potentially destroy the cell
    // and all its subexpressions
 
    // If the cell has a correspondance in the database
    // then destroy it
    if(this.model.isNew() == false) {
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

  initialize: function() {
      _.bindAll(this,'render','make','handle_active');
      this.model.bind('change:active',this.handle_active);
  },

  render: function() {
      $(this.el).html(this.model.cid);
      $(this.el).bind("contextmenu", function(e) {
        return false;
      });
      return this;
  },

  toggle_visible: function(e) {
    //Right click - Toggle visibility of the cell
    if(e.button == 2) {
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

  handle_active: function(cell,is_active) {
      active_cell = cell;
      if(is_active) {
          // Acts on the CellView object of the model
          this.model.view.set_active(true);
      } else {
          this.model.view.set_active(false);
      }
  }

});

var NodeSelectionView = Backbone.View.extend({

  tagName: "button",

  className: 'button',

  events: {
     "click": "unselect",
     "mouseover": "highlight",
     "mouseout": "unhighlight",
  },

  css3effect: false,

  initialize: function() {
      _.bindAll(this,'render','make','unselect');
      this.model.bind('change:selected',this.unselect);
      selection.getByCid(this.model.cid).view = this;
  },

  render: function() {
      $(this.el).html(this.model.get('type'));
      return this;
  },

  unselect: function(e) {
      selection.remove(this.model);
      $(this.el).remove();
  },

  highlight: function(e) {
      if(this.css3effect) {
          $('.MathJax_Display').addClass('modal');
          typsets = this.model.dom().find('.MathJax_Display');
          _.each(typsets,function(t) {
            $(t).removeClass('modal'); 
          });
          this.model.dom().addClass('shadow');
          this.model.dom().removeClass('selected');
      } else {
          this.model.dom().addClass('highlight');
      }
  },

  unhighlight: function(e) {
      if(this.css3effect) {
          $('.MathJax_Display').removeClass('modal');
          this.model.dom().removeClass('shadow');
      } else {
          this.model.dom().removeClass('highlight');
      }
  },

});
