/*
 Wise
 Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
*/


function no_match(args) {
    notify("Cannot resolve arguments to rule.");
}

function add_shift(e) {

    // TODO: use currying for this
    function add_rule(args) {
        return function() {
            apply_rule('eq_add', args);
        };
    }

    fst = Wise.Selection.at(0);
    snd = Wise.Selection.at(1);

    var selection_types = Wise.Selection.pluck('type');

    selection_pattern = Match(
            [ 'Equation', String ], add_rule( [fst, snd] ),
            [ String, 'Equation' ], add_rule( [snd, fst] ),
            ['Equation']          , no_match,
            [ String ],             add_rule( [get_root(fst), fst] )
    );

    selection_pattern(selection_types);
    e.preventDefault();
}

function sub_shift(e) {
    var node = Wise.Selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('eq_sub', [root, node]);
        value = val;
    } else {
        node.errorFlash();
    }
    e.preventDefault();
}

function mul_shift(e) {

    // TODO: use currying for this
    function add_rule(args) {
        return function() {
            apply_rule('eq_mul', args);
        }
    }

    fst = Wise.Selection.at(0);
    snd = Wise.Selection.at(1);

    var selection_types = Wise.Selection.pluck('type');

    selection_pattern = Match(
            [ 'Equation', String ], add_rule( [fst, snd] ),
            [ String, 'Equation' ], add_rule( [snd, fst] ),
            ['Equation']          , no_match,
            [ String ],             add_rule( [get_root(fst), fst] )
    );

    selection_pattern(selection_types);
    e.preventDefault();
}

function div_shift(e) {
    // TODO: use currying for this
    function add_rule(args) {
        return function() {
            apply_rule('eq_div', args);
        }
    }

    fst = Wise.Selection.at(0);
    snd = Wise.Selection.at(1);

    var selection_types = Wise.Selection.pluck('type');

    selection_pattern = Match(
            [ 'Equation', String ], add_rule( [fst, snd] ),
            [ String, 'Equation' ], add_rule( [snd, fst] ),
            ['Equation']          , no_match,
            [ String ],             add_rule( [get_root(fst), fst] )
    );

    selection_pattern(selection_types);
    e.preventDefault();
}

function select_parent(clear) {
    var start = Wise.Selection.last();

    if(!start) {
        return;
    }
    
    if(start.get('toplevel')) {
        return;
    }

    var parent = start._parent;

    if(parent && (parent.cid != start.cid)) {
        if(clear) {
            base_mode();
        }
        parent.select();
    }

}

function select_child(clear) {
    var start = Wise.Selection.last();

    if(!start) {
        return;
    }
    
    if(!start.hasChildren()) {
        return;
    }

    var child = start.children[0];
    if(child) {
        if(clear) {
            base_mode();
        }
        child.select();
    }
}

function select_next_sibling(clear) {
    var start = Wise.Selection.last();

    if(!start || !start._parent.children) {
        return;
    }

    var next = start._parent.children[start.index+1];

    if(next) {
        if(clear) {
            base_mode();
        }
        next.select();
    } 
    //else {
    //    select_parent(clear);
    //}
}

function select_prev_sibling(clear) {
    var start = Wise.Selection.last();

    if(!start || !start._parent.children) {
        return;
    }

    var prev = start._parent.children[start.index-1];

    if(prev) {
        if(clear) {
            base_mode();
        }
        prev.select();
    }
    //else {
    //    select_parent(clear);
    //}
}

function select_last_node() {
    Wise.last_expr.toggleSelect();
}

function select_root(clear) {
    var start = Wise.Selection.last();

    if(!start) {
        return;
    }

    var root = start.tree.root;

    if(root && (root.cid != start.cid)) {
        if(clear) {
            base_mode();
        }
        root.select();
    }
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

        var sub = Wise.Selection.detect(is_not_placeholder);
        if(!sub) return;

        var phs = Wise.Selection.select(is_placeholder);
        var tr_name = 'base/PlaceholderSubstitute';

        if(!phs) {
            return;
        }

        // Don't let the user subsitute a toplevel element into
        // placeholder
        if(sub.get('toplevel')) {
//            sub.errorFlash();
            return;
        }

        var queue = [];

        _.each(phs, function(ph) {
            queue.push(
                async.apply(apply_transform, tr_name, [ph, sub])
            );
        });

        async.series(queue);
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
            // Destroy the object in it's cell's expression list
            // so that saveExpresions in the cell won't try and
            // do a PUT request for it anymore
            elem.getCell()._expressions[elem.get('index')] = null;

        } else {
            apply_transform('base/Delete', [elem]);
        }

    });
}

function subs(obj) {
    if(Wise.Selection.length > 0) {
        apply_transform(
            'base/PlaceholderSubstitute',
            [Wise.Selection.at(0), obj]
        );
    } else {
        return;
    }
}

function save_worksheet(e) {
    Wise.Worksheet.saveAll();
    e.preventDefault();
}

function next_placeholder() {
    ph = Wise.Nodes.detect(is_placeholder);

    // If we found one and its not already selected
    if(ph && !ph.get('selected')) {
        ph.select();
        return;
    }
}
