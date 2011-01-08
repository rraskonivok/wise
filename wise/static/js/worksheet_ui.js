function palette(num) {
    if(num == 1) {
        $('#math_palette').show();
        $('#rules_palette').hide();
        $('#tab_math_palette').addClass('active');
        $('#tab_rules_palette').removeClass('active');
    }
    else {
        $('#math_palette').hide();
        $('#rules_palette').show();
        $('#tab_rules_palette').addClass('active');
        $('#tab_math_palette').removeClass('active');
    }
}

function toggle_cmdline() {
    Wise.CmdLine.toggleVisible();
}

function hide_tooltips() {
    $('[qtip]').hide();
}

// Set the interface from quasimode into base mode.
function base_mode() {
    $('#quasimode-indicator').fadeTo('fast',0.1);
    $('#basemode-indicator').fadeTo('fast',1);
    $("#selectionlist").empty();
    Wise.Selection.clear();
    Wise.CmdLine.hide();
}
