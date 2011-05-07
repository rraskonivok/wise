/*
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
*/

function test_mathml() {
    // Check whether the users browser support MathML
    var mml_namespace = "http://www.w3.org/1998/Math/MathML";
    var test1 = document.createElementNS;
    var test2 = document.createElementNS(mml_namespace, "mn");
    var test3 = test2.isDefaultNamespace(document.namespaceURI);
    return !!test1 && !!test2 && !!test3;
}

function progress(val) {
    $("#progressbar").progressbar({
        value: val
    });

    if(val >= 100) {
        $("#progressbar").addClass('hidden');
    }
}

function prompt() {

    $("#progressbar").removeClass('hidden');
    progress(10);

    $("#dialog").removeClass('hidden');
    $("#dialog").dialog({
        resizable: false,
        height:300,
        width: 350,
        modal: true,
        position: 'center',
        buttons: {
            // Ignore browser check and proceed
            "Proceed Anyways": function() {
                $( this ).dialog( "close" );
                boot();
            },
            "Go Back": function() {
                history.go(-1);
            }
        }
    });
}

///////////////////////////////////////////////////////////
// Term Lookup Table
///////////////////////////////////////////////////////////

// Takes the inital JSON that Django injects into the page in the
// variable JSON_TREE and calls build_tree_from_json to initialize
// the term database
function init_nodes() {
    Wise.Worksheet = new WorksheetModel();
    Wise.Selection = new NodeSelectionManager();
    Wise.Nodes = new Backbone.Collection();

    _.each(JSON_TREE, function (cell_json) {
        var new_cell = build_cell_from_json(cell_json);
        Wise.Worksheet.add(new_cell);
    });
}

function init_keyboard_shortcuts() {

    var doc = $(document);
    var key_template = _.template("<kbd>{{kstr}}</kbd>");
    var accel_template = _.template("<dt>{{label}}</dt><dd>{{keys}}</dd>");

    if(!Wise.Accelerators) {
        return;
    }

    // TODO: this function is a good canidate for memoiziation
    // with a localstorage cache
    Wise.Accelerators.each(function(shortcut) {

        keys = shortcut.get('keys');
        doc.bind('keydown',
            shortcut.get('keys'),
            shortcut.get('action')
        );
        var key_strokes = shortcut.get('keys').split('+');

        var accel = _.map(key_strokes, function(kstr){
            return key_template({kstr: kstr});
        }).join('+');

        var list_item = accel_template({
            label: shortcut.get('name'),
            keys: accel,
        });

        $("#keys_palette .list").append(list_item);
    });

}
