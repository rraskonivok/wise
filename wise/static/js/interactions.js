function add_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('add_to_both_sides', [root, node]);
    } else {
        error('Could not find toplevel expression');
    }
}

function sub_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('sub_from_both_sides', [root, node]);
    } else {
        error('Could not find toplevel expression');
    }
}

function mul_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('mul_both_sides', [root, node]);
    } else {
        error('Could not find toplevel expression');
    }
}

function div_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('div_both_sides', [root, node]);
    } else {
        error('Could not find toplevel expression');
    }
}

//Select the toplevel element
function select_parent(clear) {
    var start = selection.last();
    
    if(start.toplevel) {
        return;
    }

    if(clear) {
        base_mode();
    }

    get_parent(start).select();
}

function select_root(clear) {
    var start = selection.last();

    if(clear) {
        base_mode();
    }

    get_root(start).select();
}

function iter_left() {
    // Get the largest addition container
    if(selection.at(0)) {
        parents_until_not_type(selection.at(0),'Addition').select();
    }
    if(selection.at(1)) {
        return apply_rule('iter_left',[selection.at(1),selection.at(0)]);
    }
}

function select_left_root(clear) {
    var start = selection.last();

    if(clear) {
        base_mode();
    }

    select_term(get_lhs(start)); 
}

function select_right_root(clear) {
    var start = selection.last();

    if(clear) {
        base_mode();
    }

    select_term(get_rhs(start)); 
}

// ( Placeholder, Placeholder , ... , Expression )
function placeholder_substitute() {
    if (selection.length >= 2) {
        var heads = selection.first(selection.length - 1);
        var last = selection.last();

        if(last.get('toplevel')) {
            error('Cannot substitute toplevel element into expression');
            return;
        }

        stream_of_phs = _.all(heads, 
            function(s) {
                return s.get('type') == 'Placeholder';
            }
        );

        if(stream_of_phs) {
            _.each(heads, function(slt) {
                apply_transform('base/PlaceholderSubstitute',[slt,last]);
            });
        }
    }
}

// ( Definition, Definition , ... , Expression )
function definition_apply() {
    if (selection.count == 2) {
        fst = selection.nth(0);
        snd = selection.nth(1);

        if(fst.is_definition() && !snd.is_definition()) {
            apply_def(fst,[snd]);
        }
    }
}

