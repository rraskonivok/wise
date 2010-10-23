function init_keyboard_shortcuts() {

    $(document).bind( 'keydown', 'f4', function() {show_debug_menu()})
        .bind('keydown', 'del', function() {remove_element()})
        .bind('keydown', 'd', function() {remove_element()})
        .bind('keydown', 'esc', function() {clear_selection()})
        .bind('keydown', 'r', function() {refresh_jsmath()})
        .bind('keydown', 'w', function() {next_placeholder()})
        .bind('keydown', 'o', function() {new_line('eq')})
        .bind('keydown', 's', function() {apply_rule('algebra_normal',null)})
        .bind('keydown', 'c', function() {apply_rule('commute_elementary',null)})
        // Variable substitutions 
        .bind('keydown', 'x', function() {use_infix('x')})
        .bind('keydown', 'y', function() {use_infix('y')})
        .bind('keydown', 'z', function() {use_infix('z')})
        .bind('keydown', 't', function() {use_infix('t')})
        // Operation substitutions
        .bind('keydown', '+', function() {use_infix('ph+ph')})
        .bind('keydown', '/', function() {use_infix('ph/ph')})
        .bind('keydown', '*', function() {use_infix('ph*ph')})
        .bind('keydown', '-', function() {use_infix('ph-ph')})
        .bind('keydown', '^', function() {use_infix('ph^ph')})
        // Number substitutions
        .bind('keydown', '2', function() {use_infix('2')})
        .bind('keydown', '1', function() {use_infix('1')})
        .bind('keydown', '0', function() {use_infix('0')})
        .bind('keydown', 'ctrl+space', function() {toggle_cmdline()}
    );

}
