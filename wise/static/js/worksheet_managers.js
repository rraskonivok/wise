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

var MenuController = Backbone.Controller.extend({

    routes: {
        "save"       : "save",
        "showsexp"   : "showsexp",
        "showobj"    : "showobj",
        "flushqueue" : "flushqueue",
        "reconnect" : "reconnect",
    },

    save: function() {
        Wise.Worksheet.saveAll();
        notify.info('Saved.');
        window.location.hash = null;
    },

    showsexp: function() {
        var tmp = "<pre>$0<pre>";
        var sexps = Wise.Selection.sexps();
        dialog_html(tmp.t(JSON.stringify(sexps,null,'\t')));
        window.location.hash = null;
    },

    showobj: function() {
        var tmp = "<pre>$0<pre>";
        var objs = Wise.Selection;
        dialog_html(tmp.t(JSON.stringify(objs,null,'\t')));
        window.location.hash = null;
    },

    flushqueue: function() {
        notify.info('Task Queue flushed.');
        window.location.hash = null;
    },

    reconnect: function() {
        Wise.Socket.disconnect();
        Wise.Socket.socket.connect();

        window.location.hash = null;
    },

});
