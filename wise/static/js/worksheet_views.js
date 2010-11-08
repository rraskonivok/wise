var CellSelection = Backbone.View.extend({

  tagName: "a",

  className: 'active',

  events: {
     "click": "toggle_visible"
  },

  initialize: function() {
      this.model.bind('change', this.render);
      _.bindAll(this,'render','make');
  },

  render: function() {
      $(this.el).html(this.model.cid);
      return this;
  },

  toggle_visible: function(e) {
    $('#'+this.model.cid).toggle();
    $(this.el).toggleClass('active');
  },

});

var NodeSelection = Backbone.View.extend({

  tagName: "a",

  className: 'active',

  events: {
     "click": "toggle_visible"
  },

  initialize: function() {
      this.model.bind('change', this.render);
      _.bindAll(this,'render','make');
  },

  render: function() {
      $(this.el).html(this.model.cid);
      return this;
  },

  toggle_visible: function(e) {
    $('#'+this.model.cid).toggle();
    $(this.el).toggleClass('active');
  },

});
