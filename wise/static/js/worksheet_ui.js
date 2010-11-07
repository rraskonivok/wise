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

function make_tooltips() {
    $('[title]').qtip({ 
        style: { 
            name: 'cream', 
            tip: true 
        }, 
    });
}
