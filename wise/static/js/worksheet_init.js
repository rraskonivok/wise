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

// Initialize the worksheet boot sequence
function init() {

    // Test for MathML support, if not then prompt the user
    if(test_mathml()) {
        boot();

    } else {

        if(!($.browser.mozilla)) {
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
    }


}

function boot() {
    // Build the node database
    init_nodes();

    // Bind keyboard shortcuts
    init_keyboard_shortcuts();

    // Load sidebar palettes
    load_math_palette();
    load_rules_palette();

    // Initialize Views
    Wise.Sidebar = new SidebarView({
        el: $("#worksheet_sidebar")
    });

    // Error logging
    Wise.Log = new Logger();

    Wise.Log.view =  new LoggerView({
        el: $('#terminal_palette'),
        model: Wise.Log,
    });

    // Heartbeat function
    //if(Wise.Settings.get('SERVER_HEARTBEAT')) {
    //    setInterval( "heartbeat()", 10000 );
    //}

    // Error logging
    Wise.CmdLine = new CmdLineView({
        el: $("#cmd"),
    });

    $("#container").show();

    layout = rearrange();
    //layout.resetOverflow();

    mkautocomplete();

    $(".noselect").disableSelection();
    $("#worksheet").show();

    // Handle unsaved changes before leaving page
    window.onbeforeunload = function(e)
    {
        e = e || window.event;
        if (Wise.Worksheet.hasChangesToCommit())
        {
            // For IE and Firefox
            if (e)
            {
                e.returnValue = "You have unsaved changes.";
            }
            // For Safari
            return "You have unsaved changes.";
        }
    };

    new WorkspaceController();
    Backbone.history.start();

    // Disable right click context menu
    $(document).bind("contextmenu",function(e){
        return false;
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
