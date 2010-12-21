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
        keys: 't',
        name: 'Insert Variable t',
        action: _infix('t'),
    },

    {
        keys: 'd',
        name: 'Remove Element',
        action: remove_element,
    },

    {
        keys: 's',
        name: 'Reduce to Algebraic Normal Form',
        action: _rule('algebra_normal'),
    },

    {
        keys: 'esc',
        name: 'Clear Selection',
        action: base_mode,
    },

    {
        keys: 'alt+a',
        name: 'Add to Both Sides of Equality',
        action: add_shift,
    },

    {
        keys: 'alt+m',
        name: 'Multiply Both Sides of Equality',
        action: mul_shift,
    },

    {
        keys: 'alt+d',
        name: 'Divide Both Sides of Equality',
        action: div_shift,
    },

    {
        keys: 'alt+s',
        name: 'Subtract from Both Sides of Equality',
        action: sub_shift,
    },

    {
        keys: '+',
        name: 'Addition',
        action: _infix('ph+ph'),
    },

    {
        keys: '-',
        name: 'Unary Negation',
        action: _infix('-ph'),
    },

    {
        keys: '*',
        name: 'Multiplication',
        action: _infix('ph*ph'),
    },

    {
        keys: '/',
        name: 'Division',
        action: _infix('ph/ph'),
    },

    {
        keys: '1',
        name: 'Insert 1',
        action: _infix('1'),
    },

    {
        keys: '2',
        name: 'Insert 2',
        action: _infix('2'),
    },

    {
        keys: '0',
        name: 'Insert 0',
        action: _infix('0'),
    },
    
    {
        keys: 'ctrl+space',
        name: 'Quick Insert',
        action: toggle_cmdline,
    },

    {
        keys: 'shift+v',
        name: 'Select Top Parent',
        action: select_root,
    },
    
    {
        keys: 'w',
        name: 'Select Next Placeholder',
        action: next_placeholder,
    },

    {
        keys: 'ctrl+s',
        name: 'Save Worksheet',
        action: save_worksheet,
    },

    {
        keys: 'p',
        name: 'Select Parent',
        action: select_parent,
    },

    {
        keys: 'c',
        name: 'Commute Elementary Operations',
        action: _rule('commute_elementary'),
    },

    {
        keys: 'e',
        name: 'Algebra Expand',
        action: _rule('algebra_expand'),
    },

]);



function init_keyboard_shortcuts() {

    var doc = $(document);
    var key_template = _.template("<kbd>{{kstr}}</kbd>");
    var accel_template = _.template("<dt>{{label}}</dt><dd>{{keys}}</dd>");

    // TODO: this function is a good canidate for memoiziation
    // with a localstorage cache
    
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

}
