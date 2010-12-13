function show_pnths() {
   var node = Wise.Selection.at(0);
   node.view.el.children('.pnths').toggle(); 
   resize_parentheses(node);
}

function add_shift() {
    var node = Wise.Selection.at(0);
    var root = get_root(node);
    if(node && root) {
        apply_rule('eq_add', [root, node]);
    } else {
        node.errorFlash();
    }
}

function sub_shift() {
    var node = Wise.Selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('eq_sub', [root, node]);
        value = val;
    } else {
        node.errorFlash();
    }
}

function mul_shift() {
    var node = Wise.Selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('eq_mul', [root, node]);
    } else {
        node.errorFlash();
    }
}

function div_shift() {
    var node = Wise.Selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('eq_div', [root, node]);
    } else {
        node.errorFlash();
    }
}

//Select the toplevel element
function select_parent(clear) {
    var start = Wise.Selection.last();
    
    if(start.toplevel) {
        return;
    }

    if(clear) {
        base_mode();
    }

    get_parent(start).select();
}

function select_root(clear) {
    var start = Wise.Selection.last();

    if(clear) {
        base_mode();
    }

    get_root(start).select();
}

function iter_left() {
    // Get the largest addition container
    if(Wise.Selection.at(0)) {
        parents_until_not_type(Wise.Selection.at(0),'Addition').select();
    }
    if(Wise.Selection.at(1)) {
        return apply_rule('iter_left',[Wise.Selection.at(1), Wise.Selection.at(0)]);
    }
}

function select_left_root(clear) {
    var start = Wise.Selection.last();

    if(clear) {
        base_mode();
    }

    get_lhs(start).select();
}

function select_right_root(clear) {
    var start = Wise.Selection.last();

    if(clear) {
        base_mode();
    }

    get_rhs(start).select(); 
}

function is_placeholder(node) {
    return node.get('type') == 'Placeholder';
} 

function is_not_placeholder(node) {
    return node.get('type') != 'Placeholder';
} 

function is_toplevel(node) {
    return node.get('toplevel');
} 

substitute_stoplist = ['Placeholder'];

// ( Placeholder, Placeholder , ... , Expression )
function placeholder_substitute() {
    if (Wise.Selection.length >= 2) {

//        if(last.get('toplevel')) {
//            //error('Cannot substitute toplevel element into expression');
//            last.errorFlash();
//            return;
//        }

        var sub = Wise.Selection.detect(is_not_placeholder);
        if(!sub) return;

        var phs = Wise.Selection.select(is_placeholder);

        var tr_name = 'base/PlaceholderSubstitute';

        queue = [];

        _.each(phs, function(ph) {
            queue.push(
                async.apply(apply_transform, tr_name, [ph, sub])
            );
        });

        async.parallel(queue);
    }
}

// ( Definition, Definition , ... , Expression )
function definition_apply() {
    if (Wise.Selection.count == 2) {
        fst = Wise.Selection.nth(0);
        snd = Wise.Selection.nth(1);

        if(fst.is_definition() && !snd.is_definition()) {
            apply_def(fst,[snd]);
        }
    }
}

function remove_element() {
    Wise.Selection.each(function(elem) {

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
    if(Wise.Selection.length > 0) {
        apply_transform('base/PlaceholderSubstitute',[Wise.Selection.at(0), obj]);
    } else {
        error('Select an object to substitute into.');
    }
}

function save_worksheet(e) {
    Wise.Worksheet.saveAll();
    e.preventDefault();
}
