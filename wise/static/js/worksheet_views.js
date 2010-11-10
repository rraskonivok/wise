var CellSelection = Backbone.View.extend({

  tagName: "a",

  className: 'active',

  events: {
     "mousedown": "toggle_visible"
  },

  initialize: function() {
      //this.model.bind('change', this.render);
      _.bindAll(this,'render','make');
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
        $(this.el).toggleClass('active');
        e.preventDefault();
        return false;
    //Left click - Select cell
    } else {
        active_cell = this.model;
        this.model.dom().toggleClass('active');
    }
  },

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
      console.log('unselect')
      selection.remove(this.model);
      //this.model.dom().removeClass('highlight');
      //this.model.set({selected: false});
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
