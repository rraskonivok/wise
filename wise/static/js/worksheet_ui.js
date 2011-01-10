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

//TODO: This still doesn't work
//$(window).scroll(function() {
//    var $sidebar = $("#worksheet_sidebar");
//    var offset = $sidebar.offset();
//    var topPadding = 20;
//    var $window = $(window);
//
//    if ($window.scrollTop() > offset.top) {
//        $sidebar.css({
//            top: $window.scrollTop() - offset.top + topPadding,
//        });
//    } else {
//        $sidebar.css({
//           top: 20,
//        });
//    }
//});


