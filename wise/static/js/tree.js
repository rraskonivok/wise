///////////////////////////////////////////////////////////
// Expression Tree Handling
///////////////////////////////////////////////////////////
//
// These models are what make *everything* on the clientside run,
// they all inherit from Backbone.js Models or Collections. In
// principle most of these are your standard n-trees and most of
// the algorithms are fairly naive, but in practice they work
// fine
//
// See: http://xw2k.nist.gov/dads//HTML/tree.html
//                                                                 
//  -----------------------------------------------------------   
//  |                      Worksheet                          |                   
//  |---------------------------------------------------------|   
//  |           Cell           |             Cell             |             
//  |                          |                              |  
//  |---------------------------------------------------------|   
//  |                          |                              |  
//  |         Equation         |           Equation           |  
//  |                          |                              |  
//  |                          |                              |  
//  |         Equation         |           Equation           |  
//  |                          |                              |  
//  |            .             |              .               |  
//  |            .             |              .               |  
//  |            .             |              .               |  
//  |                          |                              |  
//  -----------------------------------------------------------   
//                                                                
//  As a graph the structure of the workshet looks like:                                                              
//                                                                
//               Worksheet                                    
//                   |                               
//                  / \                              
//                 /   \                             
//               Cell  Cell  ...                                 
//                |                                  
//                |          .                       
//         Expression Tree    .                             
//                |            .                       
//                |                                   
//            Expression ( toplevel Node i.e Equation )
//                |                                   
//               / \
//              /   \                              
//            LHS   RHS  ( Child expression Nodes )
//             |     |
//             .     .
//             .     .
//             .     .

var Worksheet = Backbone.Collection.extend({
    url: '/ws',

    initialize: function() { 
        this.url = '/ws/' + WORKSHEET_ID;
        this.id = WORKSHEET_ID;
        this.children = [];
        this._parent = null;
//        this.bind('add',function() { alert('cow') });
    },

});

var Cell = Backbone.Model.extend({
//    url: '/cell',
    url: '/api/cell/',
        
    initialize: function(exs) {
        this.set({
            index: CELL_INDEX,
            workspace: WORKSHEET_ID,
            active: false,
        });

        this._expressions = [];
    },

    addExpression: function(exs) {
        exs.set({index: this._expressions.length});
        this._expressions.push(exs);
        this.change();
    },

    sexps: function() {
        return _.invoke(this._expressions, 'sexp');
    },

    dom: function() {
        return $('#'+this.cid);
    },

});


function build_tree_from_json(json_input) {
    //Build an expression from the output of the python function json_flat
    var T;

    //Lookup table which establishes a correspondance between the DOM
    //ids (i.e. cidd314 ) and the Node objects in the expression tree.

    //                                          
    //    (1)                     (3)          
    //    (2)                   /               
    //    (3)      --->  T - (1)       (5)  .....
    //    (4)                   \    /          
    //    (5)                     (2)           
    //     .                         \           
    //     .                          (4)       
    //     .
    //                                         

    for (var term in json_input) {
        term = json_input[term];

        var node = new Expression({
//            cid:      term.id,
            type:     term.type,
            toplevel: term.toplevel,
            args:     term.args,
            id:       term.sid
        });

        node.cid = term.id;
        
        if(term.toplevel) {
            node.index = 0;
        }

        if(!NODES.getByCid(node.cid)){
            NODES.add(node);
        }
    }

    //Iterate through the children and lookup their corresponding
    //nodes and attach to tree
    for (term in json_input) {
        var index = term;
        var term = json_input[term];
        var prent = NODES.getByCid(term.id);

        if (index == 0) {
            T = new ExpressionTree(prent);
            T.set({
                sexp: 'testing',
                annotation: 'was here',
            })
        }


        for (var child in term.children) {
            child = term.children[child];
            prent.addNode( NODES.getByCid(child) );
        }
    }

    return T;
}


var RootedTree = Backbone.Model.extend({

    initialize: function(root) { 
        root.tree = this; 
        root.depth = 1;
        root._parent = this;

        this.tree = this;
        this.nodes = []
        this.levels = [];
        this.depth = 0;

        this.root = root;
        this.levels[0] = [root];
    },


    walk: function() {

        if (!node) {
            node = this.root;
        }

        if (node.hasChildren()) {
            for (child in node.children) {
                this.walk(node.children[child]);
            }
        }

    },
});

ExpressionTree = RootedTree.extend({
    
    url: '/api/exp/',

    sexp: function () {
        return this.root.sexp();
    },


});

// This a generic Node ( of which ExpressionNode ) inherits.
var Node = Backbone.Model.extend({
    url: '/eq',
    tree: null,
    depth: null,

    initialize: function() { 
        this.children = [];
        this._parent = null;
    },

    dom: function() {
        return $('#'+this.cid);
    },

    hasChildren: function () {
        return this.children.length > 0;
    },

    treeIndex: function() {
        if(this.get('toplevel')) {
            this._treeindex = [0];
            return this._treeindex;
        } else {
            //Clone the parent's treeIndex
            this._treeindex = this._parent.treeIndex().splice(0);
            this._treeindex.push(this.index);
            return this._treeindex;
        }
    },

    //     O           O  
    //    / \   ->   / | \ 
    //   O   O      O  O  O
    addNode: function(node) {
        if (this.tree.depth < this.depth + 1) {
            this.tree.depth = this.depth + 1;
            this.tree.levels[this.depth] = [];
        }

        node.tree = this.tree;
        node.depth = this.depth + 1;
        node._parent = this;
        node.index = this.children.length;

        this.children.push(node);
        (this.tree.levels[node.depth - 1]).push(node);

        this.childrenChanged();
    },

    //      O           O   
    //    / | \   ->   / \  
    //   O  O  O      O   O 
    delNode: function() {
        // The node is about to be destroyed so fire any ui events
        // that occur when a node is unselected
        this.set({selected: false});

        // Destroy all callbacks
        this.unbind();

        //Eat up the node's children recursively
        _.invoke(this.children,'delNode');

        //Destroy the node itself
        NODES.remove(this);
    },

    //         O          O   
    // <O> +  / \   ->   / \  
    //       O   O      O  <O> 
    swapNode: function(newNode) {
        //This is your standard tree graft

        newNode._parent = this._parent;
        newNode.index = this.index;
        newNode.depth = this.depth;
        newNode.tree = this.tree;
        newNode.toplevel = this.toplevel;

        if(this._parent.children) {
            // Assign the new node the index of the old node 
            // and inform the parent
            this._parent.children[this.index] = newNode;
            this._parent.childrenChanged();
        }

        this.delNode();
    }

});

var Expression = Node.extend({
    _math: [],

    childrenChanged: function() {
        console.log('math changed');
        this.msexp();
    },

    //Generates the array of strings which is compiled iff we
    //need to get a sexp.
    msexp: function() {
        var head = this.get('type')

        // Recursivly apply msexp on the children and flatten the
        // array
        if(!this.hasChildren()) {
            this._math = sexp(head, this.get('args'));
        } else {
            this._math = sexp(head, _.invoke(this.children,'msexp') );
        }
        return this._math;
    },

    sexp: function() {
//        if(this._math.length == 0) { this.msexp(); }

        //TODO: REMOVE THIS!!!!!
        this.msexp();

        return _.flatten(this._math).join(' ')
    },

});

// Utilities for JSON <-> Expression Trees

/// Initialize a cell and all its attached nodes from a JSON
// represenattion of the cell generateed by json_flat(PyCell)
function build_cell_from_json(json_input) {
    var cell_spec = json_input[0];
    var eqs_json = json_input[1];
    var new_cell = new Cell();
    new_cell.cid = cell_spec.cid;
    new_cell.set({id: cell_spec.id})

    _.each(eqs_json, function(eq_json) {
            var expr_tree = build_tree_from_json(eq_json);
            expr_tree.cell = new_cell;

            expr_tree.set({cell: new_cell.id});
            expr_tree.set({index: 3});

            new_cell.addExpression(expr_tree);
    });

    return new_cell;
}

//Graft a tree onto a node.
function graft_tree_from_json(old_node, json_input, transformation) {
    var newtree = build_tree_from_json(json_input);

    if (!old_node) {
        //error('Could not attach branch');
        return;
    }
    old_node.msexp();
    newtree.root.transformed_by = transformation;
    newtree.root.prev_state = old_node.sexp();

    old_node.swapNode(newtree.root);
}

function sexp(head, args) {
    // Builds an array of the form (head arg[1] arg[2] ...)
    return _.flatten(['(', head, args, ')']);
}

function garbage_collect() {
    // This is sort of expensive since it involves #(NODES.length)
    // of jquery lookups, don't call it much.
    NODES.each( function(node) {
        if(!node.dom()) {
            window.log('Garbage collecting',node.cid);
            NODES.del(node);
        }
    });
}

// Tree Traversal
function get_parent(node) {
    return node._parent;
}

function get_root(node) {
    if(!node.tree) {
        window.log('Node is unattached',node);
        return;
    }
    if(node.get('toplevel') != true) {
        return get_root(node.tree.root);
    } else {
        return node;
    }
}

// Equation Traversal
function get_lhs(node) {
    return get_root(node).children[0].children[0];
}

function get_rhs(node) {
    return get_root(node).children[1].children[0];
}
