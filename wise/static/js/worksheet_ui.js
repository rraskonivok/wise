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

function show_cmdline() {
   $('.cmd').fadeIn();
   $('#cmdinput').focus();
   cmd_visible = 1;
}

function hide_cmdline() {
   $('.cmd').fadeOut();
   $('#cmdinput').focus();
   cmd_visible = 0;
}

function toggle_cmdline() {
    //Flip visibility bit

    if(cmd_visible) {
        hide_cmdline();
    } else {
        show_cmdline();                 
    }
    
    cmd_visible = cmd_visible ^ 1;
}

active_tooltips = [];

function make_tooltips(obj) {

    if(!obj) {
       obj = $('*[title]'); 
    }

    $(obj).qtip({ 
        style: { 
            name: 'cream', 
            tip: true,
        }, 
        hide: { when: { event: 'inactive' }, delay: 1000 }
    });
    active_tooltips.push($(obj).qtip);
}

function hide_tooltips() {
    $('[qtip]').hide();
}

// Set the interface from quasimode into base mode.
function base_mode() {
    $('#quasimode-indicator').fadeTo('fast',0.1);
    $('#basemode-indicator').fadeTo('fast',1);
    hide_tooltips();
    selection.clear();
    hide_cmdline();
    ctrlPressed = false;
}

active_cells = {};
