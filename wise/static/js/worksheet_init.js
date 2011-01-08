function test_mathml() {
    // Check whether the users browser support MathML
    var mml_namespace = "http://www.w3.org/1998/Math/MathML";
    var test1 = document.createElementNS;
    var test2 = document.createElementNS(mml_namespace, "mn");
    var test3 = test2.isDefaultNamespace(document.namespaceURI);
    return !!test1 && !!test2 && !!test3;
}

function init() {

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
    //TODO: move this into its own worker thread
    init_nodes();
    init_keyboard_shortcuts();
    load_math_palette();
    load_rules_palette();

    // Initialize Views
    Wise.Sidebar = new SidebarView({
        el: $("#worksheet_sidebar")
    });

    Wise.Log = new Logger();

    Wise.Log.view =  new LoggerView({
        el: $('#terminal_palette'),
        model: Wise.Log,
    });

    if(Wise.Settings.get('SERVER_HEARTBEAT')) {
        setInterval( "heartbeat()", 10000 );
    }

    Wise.CmdLine = new CmdLineView({
        el: $("#cmd"),
    });

    $("#worksheet").show();
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
