###
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
###

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
        $("#dialog").dialog
            resizable: false
            height:300
            width: 350
            modal: true
            position: 'center'
            buttons:
                # Ignore browser check and proceed
                "Proceed Anyways": ->
                    $( this ).dialog( "close" )
                    init_components()
                "Go Back": ->
                    history.go(-1)

    # ---------------------------------
    # Initalize Keyboard Bindings
    # ---------------------------------
    init_keyboard_shortcuts = ->

        doc = $(document)
        key_template = _.template("<kbd>{{kstr}}</kbd>")
        accel_template = _.template("<dt>{{label}}</dt><dd>{{keys}}</dd>")

        if not Wise.Accelerators
            return

        # TODO: this function is a good canidate for memoiziation
        # with a localstorage cache
        Wise.Accelerators.each( (shortcut) ->

            keys = shortcut.get('keys')
            doc.bind('keydown',
                shortcut.get('keys'),
                shortcut.get('action')
            )

            key_strokes = shortcut.get('keys').split('+')

            accel = _.map key_strokes, (kstr) ->
                key_template({kstr: kstr})

            accel.join('+')

            list_item = accel_template({
                label: shortcut.get('name'),
                keys: accel,
            })

            $("#keys_palette .list").append(list_item)
        )

    # ---------------------------------
    # Initalize Expression Trees
    # ---------------------------------

    # Takes the inital JSON that Django injects into the page in the
    # variable JSON_TREE and calls build_tree_from_json to initialize
    # the term database
    init_nodes = ->
        Wise.Worksheet = new WorksheetModel()
        Wise.Selection = new NodeSelectionManager()
        Wise.Nodes = new Backbone.Collection()

        for cell_json in JSON_TREE
            new_cell = build_cell_from_json(cell_json)
            Wise.Worksheet.add(new_cell)

    # ---------------------------------
    # Initalize Worksheet Views
    # ---------------------------------
    init_views = ->

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


    # -----------------------
    # Initalize Subcomponents
    # -----------------------
    init_components = ->

        # Build the node database
        init_nodes()

        # Bind keyboard shortcuts
        init_keyboard_shortcuts()

        init_views()

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

        progress(100)


    # --------------------
    # Initialize Worksheet
    # --------------------
    init = ->
        # Load sidebar palettes
        load_math_palette()
        load_rules_palette()

        layout = rearrange()
        # layout.resetOverflow();

        # Test for MathML support, if not then prompt the user
        if test_mathml()
            init_components()
        else
            if not $.browser.mozilla
                prompt()

    exports.init = init
