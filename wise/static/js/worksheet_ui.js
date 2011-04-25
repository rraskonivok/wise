/*
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
*/

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

// Set the interface from quasimode into base mode.
function base_mode() {
    //$("#selectionlist").empty();
    Wise.Selection.clear();
    Wise.CmdLine.hide();

    // MUST RETURN FALSE, otherwise Firefox cancels the active
    // XHR request, which may close the socket... which is very
    // bad
    return false;
}
