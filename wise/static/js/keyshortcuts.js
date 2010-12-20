//Convienance wrappers to return anonymous functions for common
//commands

var _infix = function(code) {
    return function() {
        use_infix(code);
    }
}

var _rule = function(rule) {
    return function() {
        apply_rule(rule);
    }
}

Wise.Accelerators = new Backbone.Collection([

    {
        keys: 'del',
        name: 'Remove Element',
        action: remove_element,
    },

    {
        keys: 'esc',
        name: 'Base Mode',
        action: base_mode,
    },

    {
        keys: 'x',
        name: 'Insert Variable x',
        action: _infix('x'),
    },

    {
        keys: 'y',
        name: 'Insert Variable y',
        action: _infix('y'),
    },

    {
        keys: 'z',
        name: 'Insert Variable z',
        action: _infix('z'),
    },

    {
        keys: 'alt+a',
        name: 'Add to Both Sides of Equality',
        action: add_shift,
    },

    {
        keys: 's',
        name: 'Reduce to Algebraic Normal Form',
        action: _rule('algebra_normal'),
    },

]);



function init_keyboard_shortcuts() {

    var doc = $(document);
    var key_template = _.template("<kbd>{{kstr}}</kbd>");
    var accel_template = _.template("<dt>{{label}}</dt><dd>{{keys}}</dd>");

    // TODO: this function is a good canidate for memoiziation
    // with a localstorage cachce

    Wise.Accelerators.each(function(shortcut) {

        keys = shortcut.get('keys');
        doc.bind('keydown', 
            shortcut.get('keys'), 
            shortcut.get('action')
        );
        var key_strokes = shortcut.get('keys').split('+');

        var accel = _.map(key_strokes, function(kstr){ 
            return key_template({kstr: kstr});
        }).join('+');

        var list_item = accel_template({
            label: shortcut.get('name'), 
            keys: accel,
        });

        $("#keys_palette .list").append(list_item);
    });

    //$(document).bind('keydown', 'del', function() {remove_element()})
    //    .bind('keydown', 'd', function() {remove_element()})
    //    .bind('keydown', 'esc', function() {base_mode();})
    //    .bind('keydown', 'r', function() {rebuild_node()})
    //    .bind('keydown', 'w', function() {next_placeholder()})
    //    .bind('keydown', 'o', function() {new_line('eq')})
    //    .bind('keydown', 'shift+/', function() {new_assum('assum')})
    //    .bind('keydown', 's', function() {apply_rule('algebra_normal',null)})
    //    .bind('keydown', 'c', function() {apply_rule('commute_elementary',null)})
    //    .bind('keydown', 'e', function() {apply_rule('algebra_expand',null)})
    //    .bind('keydown', 'p', function() {select_parent(true)})
    //    .bind('keydown', 'shift+v', function() {select_root(true)})
    //    .bind('keydown', '$', function() {select_right_root(true)})
    //    .bind('keydown', '^', function() {select_left_root(true)})
    //    .bind('keydown', 'alt+a', add_shift)
    //    .bind('keydown', 'alt+m', mul_shift)
    //    .bind('keydown', 'alt+d', div_shift)
    //    .bind('keydown', 'alt+s', sub_shift)
    //    .bind('keydown', 'ctrl+s', save_worksheet)
    //    .bind('keydown', 'shift+left', iter_left)
    //    // Variable substitutions 
    //    .bind('keydown', 'x', function() {use_infix('x')})
    //    .bind('keydown', 'y', function() {use_infix('y')})
    //    .bind('keydown', 'z', function() {use_infix('z')})
    //    .bind('keydown', 't', function() {use_infix('t')})
    //    // Operation substitutions
    //    .bind('keydown', '+', function() {use_infix('ph+ph')})
    //    .bind('keydown', '/', function() {use_infix('ph/ph')})
    //    .bind('keydown', '*', function() {use_infix('ph*ph')})
    //    .bind('keydown', '-', function() {use_infix('-ph')})
    //    //.bind('keydown', '^', function() {use_infix('ph^ph')})
    //    .bind('keydown', 'shift+I', function() {use_infix('integral ph')})
    //    .bind('keydown', 'shift+D', function() {use_infix('diff ph')})
    //    // Number substitutions
    //    .bind('keydown', '2', function() {use_infix('2')})
    //    .bind('keydown', '1', function() {use_infix('1')})
    //    .bind('keydown', '0', function() {use_infix('0')})
    //    .bind('keydown', 'ctrl+space', function() {toggle_cmdline()}
    //);

}
