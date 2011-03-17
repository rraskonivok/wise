/*
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
*/


var NodeSelectionManager = Backbone.Collection.extend({
    clear: function() {
        // Tell all the models they are no longer selected, this
        // will also cause any selection bar DOM elements to kill
        // themselves
        
        // Create a clone of the models since _.each alters the
        // elements in places
        var list = this.models.slice(0);
        
        _.each(list, function( selected ) {
            selected.unselect();
            Wise.Selection.remove( selected );
        });
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

// TODO: rename menu controller
var WorkspaceController = Backbone.Controller.extend({

    routes: {
        "save": "save", // #save
    },

    save: function() {
        Wise.Worksheet.saveAll();
        window.location.hash = null;
    },

});
