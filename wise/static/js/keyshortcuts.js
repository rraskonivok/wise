function init_keyboard_shortcuts() {

    $(document).bind( 'keydown', 'f4', function() {show_debug_menu()})
        .bind('keydown', 'del', function() {remove_element()})
        .bind('keydown', 'd', function() {remove_element()})
        .bind('keydown', 'esc', function() {base_mode();})
        .bind('keydown', 'r', function() {refresh_jsmath()})
        .bind('keydown', 'w', function() {next_placeholder()})
        .bind('keydown', 'o', function() {new_line('eq')})
        .bind('keydown', 's', function() {apply_rule('algebra_normal',null)})
        .bind('keydown', 'c', function() {apply_rule('commute_elementary',null)})
        .bind('keydown', 'e', function() {apply_rule('algebra_expand',null)})
        .bind('keydown', 'p', function() {select_parent(true)})
        .bind('keydown', 'shift+v', function() {select_root(true)})
        .bind('keydown', '$', function() {select_right_root(true)})
        .bind('keydown', '^', function() {select_left_root(true)})
        .bind('keydown', 'alt+a', function() {add_shift()})
        .bind('keydown', 'alt+m', function() {mul_shift()})
        .bind('keydown', 'alt+d', function() {div_shift()})
        .bind('keydown', 'alt+s', function() {sub_shift()})
        // Variable substitutions 
        .bind('keydown', 'x', function() {use_infix('x')})
        .bind('keydown', 'y', function() {use_infix('y')})
        .bind('keydown', 'z', function() {use_infix('z')})
        .bind('keydown', 't', function() {use_infix('t')})
        // Operation substitutions
        .bind('keydown', '+', function() {use_infix('ph+ph')})
        .bind('keydown', '/', function() {use_infix('ph/ph')})
        .bind('keydown', '*', function() {use_infix('ph*ph')})
        .bind('keydown', '-', function() {use_infix('-ph')})
        //.bind('keydown', '^', function() {use_infix('ph^ph')})
        .bind('keydown', 'shift+I', function() {use_infix('integral ph')})
        .bind('keydown', 'shift+D', function() {use_infix('diff ph')})
        // Number substitutions
        .bind('keydown', '2', function() {use_infix('2')})
        .bind('keydown', '1', function() {use_infix('1')})
        .bind('keydown', '0', function() {use_infix('0')})
        .bind('keydown', 'ctrl+space', function() {toggle_cmdline()}
    );

}
