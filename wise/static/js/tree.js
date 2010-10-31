///////////////////////////////////////////////////////////
// Expression Tree Handling
///////////////////////////////////////////////////////////

var WORKSHEET = Backbone.Collection;

var Cell = Backbone.Model;

// Lookup Table for translation between DOM objects and Node objects
NODES = new Backbone.Collection();

function RootedTree(root) {
    root.tree = this;
    root.depth = 1;
    root._parent = this;
    this.root = root;
    this.levels[0] = [root];
}

function build_tree_from_json(json_input) {
    //Build an expression from the output of the python function json_flat
    var T;

    //Lookup table which establishes a correspondance between the DOM
    //ids (i.e. uid314 ) and the Node objects in the expression tree.
    //Create a hash table: { 'uid3': Node of uid3 }

    for (var term in json_input) {
        term = json_input[term];

        var node = new Expression({
            id:       term.id,
            type:     term.type,
            toplevel: term.toplevel,
            args:     term.args,
            sid:      term.sid
        });
        
        if(term.toplevel) {
            node.index = 0;
        }

        node.dom = $('#' + node.id,"#workspace");

        NODES.add(node);
    }

    //Iterate through the children and lookup their corresponding
    //nodes and attach to tree
    for (term in json_input) {
        index = term;
        term = json_input[term];
        prent = NODES.get(term.id);

        if (index == 0) {
            T = new RootedTree(prent);
        }

        for (var child in term.children) {
            child = term.children[child];
            prent.addNode( NODES.get(child) );
        }
    }

    return T;
}

//Graft a tree onto a node.
function merge_json_to_tree(old_node, json_input, transformation) {
    var newtree = build_tree_from_json(json_input);
    if (!old_node) {
        //error('Could not attach branch');
        return;
    }
    old_node.math();
    newtree.root.transformed_by = transformation;
    newtree.root.prev_state = old_node.smath();

    old_node.swapNode(newtree.root);
}

///////////////////////////////////////////////////////////
// Term Handling
///////////////////////////////////////////////////////////
// This is the key algorithm that makes everything run, the
// properties and methods are .prototyped for speed since they are
// likely called thousands of times.

var RootedTree = Backbone.Model.extend({
    initialize: function(root) { 
        root.tree = this; 
        root.depth = 1;
        root._parent = this;
        this.root = root;
        this.levels[0] = [root];
    },
});

RootedTree.prototype.walk = function (node) {
    if (!node) {
        node = this.root;
    }
    if (node.hasChildren()) {
        for (child in node.children) {
            this.walk(node.children[child])
        }
    }
}

RootedTree.prototype.tree = this;
RootedTree.prototype.nodes = [];
RootedTree.prototype.levels = [];
RootedTree.prototype.depth = 0;

var Node = Backbone.Model.extend({

    initialize: function() { 
        this.children = [];
        this._parent = null;
    },

});

Node.prototype.tree = null;
Node.prototype.hasChildren = function () {
    return this.children.length > 0
}

Node.prototype.depth = null;

Node.prototype.addNode = function (node) {
    if (this.tree.depth < this.depth + 1) {
        this.tree.depth = this.depth + 1;
        this.tree.levels[this.depth] = [];
    }

    node.tree = this.tree;
    node.depth = this.depth + 1;
    node._parent = this
    node.index = this.children.length;

    this.children.push(node);
    (this.tree.levels[node.depth - 1]).push(node);
}

Node.prototype.delNode = function (node) {

    //Eat up the node's children recursively
    _.invoke(this.children,'delNode');
    //Destroy the node itself
    NODES.remove(this);
}

Node.prototype.treeIndex = function() {
    if(this.get('toplevel')) {
        this._treeindex = [0];
        return this._treeindex;
    } else {
        //Clone the parent's treeIndex
        this._treeindex = this._parent.treeIndex().splice(0);
        this._treeindex.push(this.index);
        return this._treeindex;
    }
}

Node.prototype.swapNode = function (newNode) {

    newNode._parent = this._parent;
    newNode.index = this.index;
    newNode.depth = this.depth;
    newNode.tree = this.tree;
    newNode.toplevel = this.toplevel;

    if(this._parent.children) {
        // Assign the new node the index of the old node 
        // and inform the parent
        this._parent.children[this.index] = newNode;
    }

    this.delNode();
}

var Expression = Node.extend({

    initialize: function(root) { 
        this.children = [];
        this._parent = null;
        this._math = [];
    }

});

//Expression.prototype = new Node();
Expression.prototype.smath = function () {
    if(this._math.length == 0) { this.math(); }
    return _.flatten(this._math).join(' ')
}

Expression.prototype.math = function() {
    var head = this.get('type')

    if(!this.hasChildren()) {
        this._math = sexp(head, this.get('args'));
    } else {
        this._math = sexp(head, _.invoke(this.children,'math') );
    }
    return this._math;
}

function sexp(head, args) {
    // Builds an array of the form (head arg[1] arg[2] ...)
    return _.flatten(['(', head, args, ')']);
}
