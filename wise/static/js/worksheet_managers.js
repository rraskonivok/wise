var NodeSelectionManager = Backbone.Collection.extend({
    // For compatibility
    nth: function(index) {
        return this.at(index);
    },

    clear: function() {
        // Tell all the models they are no longer selected, this
        // will also cause any selection bar DOM elements to kill
        // themselves
        _.each(this.models, 
            function(model) {
               model.unselect();
            }
        );
//        this.remove(this.models);
    },

    // Convenience wrappers to get the sexp of the 
    // selected nodes
    sexps: function() {
        return this.invoke('sexp');
    },

    types: function() {
        return this.pluck('type');
    },
});
