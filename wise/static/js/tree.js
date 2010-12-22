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
function build_tree_from_json(json_input, top_class) {

  //TODO: remove this ugly hack
  if (!top_class) {
    top_class = ExpressionTree;
  }

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
      type: term.type,
      toplevel: term.toplevel,
      args: term.args,
      id: term.sid
    });

    node.cid = term.id;

    var nel = $('#' + node.cid);

    var nodeview = new NodeView({
      model: node,
      el: nel,
    })

    node.view = nodeview;

    if (term.toplevel) {
      node.index = 0;
    }

    if (!Wise.Nodes.getByCid(node.cid)) {
      Wise.Nodes.add(node);
    }


  }

  //Iterate through the children and lookup their corresponding
  //nodes and attach to tree
  for (term in json_input) {
    var index = term;
    var term = json_input[term];
    var prent = Wise.Nodes.getByCid(term.id);

    if (index == 0) {
      T = new top_class(prent);
      T.set({
        annotation: ' ',
      })
    }

    for (var child in term.children) {
      child = term.children[child];
      prent.addNode(Wise.Nodes.getByCid(child));
    }
  }

  return T;
}

var RootedTree = Backbone.Model.extend({

  initialize: function (root) {
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


  walk: function () {

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

  url: function () {
    if (this.id) {
      return '/api/exp/' + this.id;
    } else {
      return '/api/exp/';
    }
  },

  sexp: function () {
    this.root.msexp();
    return this.root.sexp();
  },

});

AssumptionTree = RootedTree.extend({

  url: function () {
    if (this.id) {
      return '/api/asm/' + this.id;
    } else {
      return '/api/asm/';
    }
  },

  sexp: function () {
    this.root.msexp();
    return this.root.sexp();
  },

});

// Utilities for JSON <-> Expression Trees
/// Initialize a cell and all its attached nodes from a JSON
// represenattion of the cell generateed by json_flat(PyCell)

function build_cell_from_json(json_input) {
  var cell_spec = json_input[0];
  var eqs_json = json_input[1];
  var asms_json = json_input[2];

  var new_cell = new Cell();

  new_cell.cid = cell_spec.cid;
  new_cell.set({
    id: cell_spec.id
  })

  // The new HTML element, must exist in the DOM
  var nel = $('#' + new_cell.cid);

  new_view = new CellView({
    el: nel,
    model: new_cell,
  });

  new_cell.view = new_view;

  _.each(eqs_json, function (eq_json) {
    var expr_tree = build_tree_from_json(eq_json);
    expr_tree.cell = new_cell;

    expr_tree.set({
      cell: new_cell.id
    });
    expr_tree.cell = new_cell;
    expr_tree.set({
      index: 3
    });

    new_cell.addExpression(expr_tree);
  });

  _.each(asms_json, function (asm_json) {
    var expr_tree = build_tree_from_json(asm_json, AssumptionTree);
    expr_tree.cell = new_cell;

    expr_tree.set({
      cell: new_cell.id
    });
    expr_tree.cell = new_cell;
    expr_tree.set({
      index: 3
    });

    new_cell.addAssumption(expr_tree);
  });

  Wise.last_cell = new_cell;

  return new_cell;
}

//       E  (Expression Tree)        F  ( Different Expression Tree)
//       |                           |  
//      <A>                     →    X     
//      / \                         / \ 
//     B   C                       Y   Z
//Build a tree from a json specifiction and then then graft (
//by replacement) onto a existing expression tree.


function graft_toplevel_from_json(old_node, json_input, transformation) {
  var cell = old_node.tree.cell;
  var old_index = old_node.tree.get('index');
  var newtree = build_tree_from_json(json_input);

  newtree.root.transformed_by = transformation;
  newtree.root.prev_state = old_node.sexp();

  old_node.swapNode(newtree.root);
  newtree.set(old_node.attributes);

  //TODO: this is causing assumption grafted at the toplevel to
  //break
  cell._expressions[old_index] = newtree;
  newtree.set({
    index: old_index
  });

  newtree.cell = old_node.cell;

  return newtree;
}

//       E  (Expression Tree)        E  ( Same Expression Tree)
//       |                           |  
//      <A>                     →   <X>      
//      / \                         / \ 
//     B   C                       Y   Z
//Build a Node from a json specifiction and then then 
//graft ( by replacement ) onto a existing expression tree.
// TODO: change this to graft_node_from_json to avoid amguity
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
  return newtree;
}

function sexp(head, args) {
  // Builds an array of the form (head arg[1] arg[2] ...)
  return _.flatten(['(', head, args, ')']);
}

function garbage_collect() {
  // This is sort of expensive since it involves #(Wise.Nodes.length)
  // of jquery lookups, don't call it much.
  Wise.Nodes.each(function (node) {
    if (!node.view) {
      window.log('Garbage collecting', node.cid);
      Wise.Nodes.del(node);
    }
  });
}

// Tree Traversal
function get_parent(node) {
  return node._parent;
}

function get_root(node) {
  if (node && !node.tree) {
    window.log('Node is unattached', node);
    return;
  }
  if (node && node.get('toplevel') != true) {
    return get_root(node.tree.root);
  } else {
    return node;
  }
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
