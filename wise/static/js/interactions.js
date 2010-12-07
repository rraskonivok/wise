function show_pnths() {
   var node = selection.at(0);
   node.view.el.children('.pnths').toggle(); 
   resize_parentheses(node);
}

function add_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('eq_add', [root, node]);
    } else {
        node.errorFlash();
    }
}

function sub_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('eq_sub', [root, node]);
    } else {
        node.errorFlash();
    }
}

function mul_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('eq_mul', [root, node]);
    } else {
        node.errorFlash();
    }
}

function div_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('eq_div', [root, node]);
    } else {
        node.errorFlash();
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

    get_lhs(start).select();
}

function select_right_root(clear) {
    var start = selection.last();

    if(clear) {
        base_mode();
    }

    get_rhs(start).select(); 
}

// ( Placeholder, Placeholder , ... , Expression )
function placeholder_substitute() {
    if (selection.length >= 2) {
        var heads = selection.first(selection.length - 1);
        var last = selection.last();

        if(last.get('toplevel')) {
            //error('Cannot substitute toplevel element into expression');
            last.errorFlash();
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

function remove_element() {
    selection.each(function(elem) {

        if(elem.get('toplevel')) {
            root = get_root(elem).tree;

            // If the root has a correspondance in the database
            // then destroy it
            if(!root.isNew()) {
                root.destroy();
            }

            elem.dom().remove();
            elem.delNode();
        } else {
            apply_transform('base/Delete', [elem]);
        }

    });
}

function subs(obj) {
    if(selection.length > 0) {
        apply_transform('base/PlaceholderSubstitute',[selection.at(0), obj]);
    } else {
        error('Select an object to substitute into.');
    }
}

function save_worksheet(e) {
    WORKSHEET.saveAll();
    e.preventDefault();
}
