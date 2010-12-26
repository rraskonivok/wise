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

var RootedTree = Backbone.Model.extend({

  initialize: function (root) {
    root.tree = this;
    root.depth = 1;
    root._parent = this;

    this.root = root;
    this.tree = this;

    // A hash of all nodes in the tree, in no particular order
    this.nodes = {};
    this.nodes[root.cid] = root;

    this.depth = 0;
  },

  count: function() {
    return _.keys(this.nodes).length;
  },

  walk: function (node) {

    if (!node) {
      node = this;
    }

    if (node.hasChildren()) {
      for (child in node.children) {
        return node.walk(node.children[child]);
      }
    }
    return this;

  },
});

var TreeFragment = Backbone.Model.extend({

  initialize: function (root) {
    root.depth = 1;
    root._parent = this;

    this.root = root;

    // A hash of all nodes in the tree, in no particular order
    this.nodes = {};
    this.nodes[root.cid] = root;

    this.depth = 0;
  },

  bindToTree: function(tree) {
    for (node in this.nodes) {
        this.nodes[node].tree = tree;
    }
  },

});

// This a generic Node in a tree structure ( of which ExpressionNode inherits)
var Node = Backbone.Model.extend({
  tree: null,
  depth: null,

  url: '/eq',
//  url: function(){
//     return this.get('resource_uri') || this.collection.url;
//  }

  initialize: function () {
    this.children = [];
    this._parent = null;
  },

  //TODO: remove this, its ugly and we should be using views
  dom: function () {
    return $(this.view.el);
  },

  register: function() {
    this.tree = this._parent.tree;

    if(this.hasChildren()) {
        for(child in this.children) {
            this.children[child].register();
        }
    }

  },

  hasChildren: function () {
    return this.children.length > 0;
  },

  treeIndex: function () {
    if (this.depth === 1) {
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
  addNode: function (node, silent) {
    if (!this.tree) {
        throw 'Cannot attached to orphan node, attach parent to tree first.';
    }

    if (this.tree.depth < this.depth + 1) {
      this.tree.depth = this.depth + 1;
    }

    node.tree = this.tree;
    node.depth = this.depth + 1;
    node._parent = this;
    node.index = this.children.length;

    this.children.push(node);

    this.tree.nodes[node.cid] = node;

    if(!silent) {
        this.trigger('struct_change');
    }

  //  this.childrenChanged();
  },

  //      O           O
  //    / | \   ->   / \
  //   O  O  O      O   O
  delNode: function () {
    // The node is about to be destroyed so fire any ui events
    // that occur when a node is unselected
    this.set({
      selected: false
    });
    this.unselect();

    // Destroy all callbacks
    this.unbind();

    //Eat up the node's children recursively
    _.invoke(this.children, 'delNode');

    //Destroy the node itself
    Wise.Nodes.remove(this);

    // Tell the tree that it has changed contents and needs
    // to pushed to the server.
    delete this;
  },

  //         O          O   
  // <O> +  / \   ->   / \  
  //       O   O      O  <O> 
  swapNode: function (newNode) {
    newNode._parent = this._parent;
    newNode.index = this.index;
    newNode.depth = this.depth;
    newNode.tree = this.tree;
    newNode.toplevel = this.toplevel;

    if(this._parent.tree === null) {
        console.log('Null tree');
    }

    newNode.register();

    if (this._parent.children) {
      // Assign the new node the index of the old node 
      // and inform the parent
      this._parent.children[this.index] = newNode;
      this._parent.childrenChanged();
    }

    this.delNode();

    // Tell the tree that it has changed contents and needs
    // to pushed to the server.
  },

  //TODO: move this to the view
  errorFlash: function () {
    $(this.view.el).effect("highlight", {
      color: '#E6867A'
    }, 1000);
  },


});

// Tree Traversal
function get_parent(node) {
  return node._parent;
}

function get_root(node) {
  // This doesn't work if .tree isn't set right
  if (node && !node.tree) {
    throw 'Node is unattached';
  }
  return node.tree.root;
}

// Equation Traversal
function get_lhs(node) {
  return get_root(node).children[0];
}

function get_rhs(node) {
  return get_root(node).children[1];
}

// Traverse the tree upwards until it find a node matching
// [filter], behaves like jQuery's parents
function parents(node, filter) {
  if (node._parent) {
    var prent = node._parent;
    if (filter(prent)) {
      return node
    }
    return parents(prent, filter);
  }
}

// Traverse the tree upwards until it find a node matching
// [filter] inclusive on the matched nodee, behaves like 
// jQuery's parents
function parentsUntil(node, filter) {
  if (node._parent) {
    var prent = node._parent;
    if (filter(prent)) {
      return prent
    }
    return parents(prent, filter);
  }
}

// Traverse the tree upwards until it find a node who's 'type'
// attribute matches [type].
function parents_until_type(node, type) {
  return parentsUntil(node, function (n) {
    return n.get('type') == type;
  });
}

function parents_until_not_type(node, type) {
  return parents(node, function (n) {
    return n.get('type') != type;
  });
}
