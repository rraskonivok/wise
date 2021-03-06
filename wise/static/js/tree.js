///////////////////////////////////////////////////////////
// Expression Tree Handling
///////////////////////////////////////////////////////////

function Cell() {
    this.equations = [];
    this.length = 0;
    this.dom = null;
}

function Equation() {
    this.tree = null;
    this.cell = null;
    this.next = null;
    this.prev = null;
    this.index = null;
}

function RootedTree(root) {
    root.tree = this;
    root.depth = 1;
    root._parent = this;
    this.root = root;
    this.levels[0] = [root];
}

function build_tree_from_json(json_input) {
    //Our Expression tree
    var T;

    //Lookup table which establishes a correspondance between the DOM
    //ids (i.e. uid314 ) and the Node objects in the expression tree.
    //Craete a hash table: { 'uid3': Node of uid3 }
    for (var term in json_input) {
        term = json_input[term];
        var node = new Expression();
        NODES[term.id] = node;
        node.id = term.id;
        node.name = term.type;
        node.dom = $('#' + node.id);
    }

    //Iterate through the children and lookup their corresponding
    //nodes and attach to tree
    for (term in json_input) {
        index = term;
        term = json_input[term];
        prent = NODES[term.id]
        if (index == 0) {
            T = new RootedTree(prent)
        };
        for (var child in term.children) {
            child = term.children[child];
            //console.log(nodes[child]);
            prent.addNode(NODES[child]);
        }
    }

    return T;
}

//Nested JSON Tree (InfoVis requires this)

function recurse(node, stack_depth) {

    if (!stack_depth) {
        stack_depth = 1
    } else {
        stack_depth += 1
    }

    if (stack_depth > 25) {
        alert('fuck, maximum recursion depth reached' + $(object).attr('id') + ',group:' + $(object).attr('group'))
        return null
    }
    else {
        var json = {};
        json.id = 'node' + node.id;
        json.data = node;
        json.name = node.name;
        json.children = []

        console.log(json, stack_depth);

        for (child in node.children) {
            child = node.children[child];
            if (child) {
                json.children.push(recurse(child, stack_depth));
            }
        }

        return json
    }
}

function nested_json(T) {
    //Returns the nested JSON form a (sub)tree.
    //
    // The nested JSON is of the form:
    //  var json = {  
    //      "id": "aUniqueIdentifier",  
    //      "name": "usually a nodes name",  
    //      "data": {
    //          "some key": "some value",
    //          "some other key": "some other value"
    //       },  
    //      "children": [ 'other nodes or empty' ]  
    //  }; 
    return recurse(T.root);
}

function merge_json_to_tree(old_node, json_input) {
    var newtree = build_tree_from_json(json_input);
    if (!old_node) {
        error('Could not attach branch');
        return;
    }
    old_node.swapNode(newtree.root);

    //Swap out a node in a tree with an expression created from
    //JSON 
    //js doesn't have proper iterators *grumble, grumble*
    //if(json_input.length == 1) {
    //   var node = new Expression();
    //   var term = json_input[0];
    //   old_node.swapNode(node);
    //   //console.log("old_node: %s",old_node.id());
    //   NODES[term.id] = node; 
    //   node.id = term.id;
    //   node.name = term.type;
    //   node.dom = $('#' + term.id);
    //   //delete NODES[old_node.id()];
    //} else {
    //    for(var term in json_input) {
    //       var index = term;
    //       var term = json_input[term];
    //       var node = new Expression();
    //       if(index == 0) {
    //            old_node.swapNode(node);
    //            //console.log("old_node: %s",old_node.id());
    //            //delete NODES[old_node.id()];
    //       }
    //       NODES[term.id] = node; 
    //       node.id = term.id;
    //       node.name = term.type;
    //       node.dom = $('#' + node.id);
    //    }
    //}
}

function append_to_tree(root, json_input) {
    var newtree = build_tree_from_json(json_input);
    root.addNode(newtree.root);

    //for(var term in json_input) {
    //   var index = term;
    //   var term = json_input[term];
    //   node = new Expression();
    //   if(index == 0) {
    //        root.addNode(node);
    //     //   console.log("root_node: %s",root.id());
    //   }
    //   NODES[term.id] = node; 
    //   node.id = term.id;
    //   node.name = term.type;
    //   node.dom = $('#' + term.id);
    //}
}

///////////////////////////////////////////////////////////
// Term Handling
///////////////////////////////////////////////////////////
//This is the key algorithm that makes everything run, the
//properties and methods are .prototyped for speed since they are
//likely called thousands of times.
// This is a hash trie, see http://en.wikipedia.org/wiki/Trie
EQUATION_TREE = null;

function RootedTree(root) {
    root.tree = this;
    root.depth = 1;
    root._parent = this;
    this.root = root;
    this.levels[0] = [root];
}

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

function Node() {
    this.children = [];
    this._parent = null;
}
this.equations = [];
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
    //If the node is not the root / toplevel
    if (this.depth > 1) {
        this._parent.children.splice(this.index, 1);

        //Regenerate the indices
        for (var i = 0; i < this._parent.children.length; i++) {
            this._parent.children[i].index = i;
        }
    }
    //Eat up the node's children recursively, quite a modest
    //proposal
    for (var i = 0; i < this.children.length; i++) {
        this.children[i].delNode();
    }
    //Destroy the node itself
    delete NODES[this.id];
    delete this;
}

Node.prototype.swapNode = function (newNode) {

    console.log('newNode');
    console.log(newNode);

    newNode._parent = this._parent;
    newNode.index = this.index;
    newNode.depth = this.depth;
    newNode.tree = this.tree;
    this._parent.children[this.index] = newNode;
}

function Expression() {
/* Javascript is much faster at manipulating
    arrays than strings */

    this.children = [];
    this._parent = null;
    this._math = [];
    this.dom = null;
    this.hash = null;
}

Expression.prototype = new Node();
Expression.prototype.smath = function () {
    return this._math.join(' ')
}

/*
// O(n) , n = nodes in tree
for (level in T.levels.reverse()) {
    var terms = T.levels[level];
    for(term in terms) {
       term = terms[term]; 
       var _parent = term._parent
       if(!term.hasChildren())
       {
            term.math = term._math
       }
       else
       {
           term.math = ['(',term.mathtype,' ',term._math.join(' '),')'].join('')
       }
       _parent._math.push(term.math)
    }
}
*/
