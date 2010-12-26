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
        keys: 'k',
        name: 'Select Parent',
        action: select_parent,
    },

    {
        keys: 'j',
        name: 'Select Child',
        action: select_child,
    },

    {
        keys: 'l',
        name: 'Select Next Sibling',
        action: select_next_sibling,
    },

    {
        keys: 'h',
        name: 'Select Previous Sibling',
        action: select_prev_sibling,
    },

    {
        keys: ":",
        name: 'Select Last Node',
        action: select_last_node,
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

    {
        keys: 'shift+o',
        name: 'New Cell',
        action: new_cell,
    },

    {
        keys: 'o',
        name: 'New Cell',
        action: function() { new_line('eq', Wise.last_cell) },
    },

    //{
    //    keys: 'h',
    //    name: 'Debug',
    //    action: highlight_orphans,
    //},

]);

