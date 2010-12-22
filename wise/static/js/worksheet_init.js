function init() {

    // Warn the user if the browser doesn't support MathML
    if(!($.browser.mozilla)) {

        $("#worksheet").hide();

        $( "#dialog" ).dialog({
            resizable: false,
            height:300,
            width: 350,
            modal: true,
            position: 'center',
            buttons: {
                "Proceed Anyways": function() {
                    $( this ).dialog( "close" );
                    $("#worksheet").show();
                },
                "Go Back": function() {
                    javascript:history.go(-1);
                }
            }
        });
    }

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

    new CmdLineView({
        el: $("#cmdline"),
    });

}
