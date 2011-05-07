module 'init', (exports) ->

    test_mathml = ->

        mml_namespace = "http://www.w3.org/1998/Math/MathML"
        test1 = document.createElementNS
        test2 = document.createElementNS(mml_namespace, "mn")
        test3 = test2.isDefaultNamespace(document.namespaceURI)
        return !!test1 && !!test2 && !!test3

    progress = (val) ->

        $("#progressbar").progressbar({
            value: val
        })

        if val >= 100
            $("#progressbar").addClass('hidden')

    prompt = ->

        $("#progressbar").removeClass('hidden')
        progress(10)

        $("#dialog").removeClass('hidden')
        $("#dialog").dialog {
            resizable: false
            height:300
            width: 350
            modal: true
            position: 'center'
            buttons: {
                # Ignore browser check and proceed
                "Proceed Anyways": ->
                    $( this ).dialog( "close" )
                    boot()
                "Go Back": ->
                    history.go(-1)
                }
            }

    # Boot sequence ( a side effect of init() )
    boot = ->

        # Build the node database
        init_nodes()

        # Bind keyboard shortcuts
        init_keyboard_shortcuts()

        # Initialize Views
        Wise.Sidebar = new SidebarView({
            el: $("#worksheet_sidebar")
        })

        # Error logging
        Wise.Log = new Logger()

        Wise.Log.view = new LoggerView({
            el: $('#terminal_palette'),
            model: Wise.Log,
        })

        # Error logging
        Wise.CmdLine = new CmdLineView({
            el: $("#cmd"),
        })

        $("#container").show()

        mkautocomplete()

        # $(".noselect").disableSelection()
        $("#worksheet").show()

        # Handle unsaved changes before leaving page
        window.onbeforeunload = (e) ->
            e = e || window.event
            if Wise.Worksheet.hasChangesToCommit()
                # For IE and Firefox
                if (e)
                    e.returnValue = "You have unsaved changes."
                # For Safari
                return "You have unsaved changes."

        new WorkspaceController()
        Backbone.history.start()

        # Disable right click context menu
        #$(document).bind("contextmenu",function(e){
        #  //return false;
        #});

        # $(".textatom").editable({
        #     type: 'textarea',
        #     editClass: 'textatom',
        #     onEdit: function(content) {
        #         textarea = $(this).find('textarea')[0];

        #         textarea.style.height = 0;
        #         textarea.style.height = textarea.scrollHeight + 'px';

        #         $(this).find('textarea').unbind('keyup');

        #         $(this).find('textarea').live('keyup',function() {
        #             this.style.height = 0;
        #             this.style.height = this.scrollHeight + 'px';
        #         });
        #     },

        #     onSubmit: function(content) {
        #         // Strip HTML tags from the new content,
        #         var matchTag = /<(?:.|\s)*?>/g;
        #         content.current = content.current.replace(matchTag, "");
        #         $(this).text(content.current);
        #     },
        # });

        progress(100)


    init = ->
        load_math_palette()
        progress(20)

        # Load sidebar palettes
        load_math_palette()
        progress(20)
        load_rules_palette()
        progress(30)

        layout = rearrange()
        # layout.resetOverflow();

        # Test for MathML support, if not then prompt the user
        if test_mathml()
            boot()
        else
            if not $.browser.mozilla
                prompt()

    exports.test_mathml = test_mathml
    exports.init = init
