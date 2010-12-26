var WorksheetModel = Backbone.Collection.extend({
  url: '/ws',

//  url: function(){
//     return this.get('resource_uri') || this.collection.url;
//  }

  initialize: function () {
//   this.url = '/ws/' + Wise.Worksheet.get('id');
//   this.id = WORKSHEET_ID;
    this.children = [];
    this._parent = null;
  },

  saveAll: function () {
    this.invoke('saveCell');
  },

});

var Cell = Backbone.Model.extend({

  url: function () {
    if (this.id) {
      return '/api/cell/' + this.id;
    } else {
      return '/api/cell/';
    }
  },

//  url: function(){
//     return this.get('resource_uri') || this.collection.url;
//  }

  initialize: function (exs) {
    this.set({
      index: CELL_INDEX,
      workspace: WORKSHEET_ID,
    });

    this._expressions = [];
    this._assumptions = [];
  },

  addExpression: function (exs) {
    exs.set({
      index: this._expressions.length
    });
    this._expressions.push(exs);
  },

  addAssumption: function (asm) {
    asm.set({
      index: this._assumptions.length
    });
    this._assumptions.push(asm);
  },

  saveCell: function () {
    if (this.hasChanged() || this.isNew()) {
      this.save({
        success: Notifications.raise('COMMIT_SUCCESS'),
      });
    }
    this.saveAssumptions();
    this.saveExpressions();
  },

  // Iterate through each Expression associated 
  // with this cell and commit if their sexp
  // have changed since thel last commit
  saveExpressions: function () {
    _.each(this._expressions, function (expr) {
      if (expr.hasChanged()) {
        // Highlight the expression to give the user
        // some visual feedback on what was just
        // committed
        //expr.root.dom().effect("highlight", {}, 1500);

        expr.set({
          sexp: expr.sexp()
        });
        expr.save({
          success: Notifications.raise('COMMIT_SUCCESS'),
        });
      }
    });
  },

  saveAssumptions: function () {
    _.each(this._assumptions, function (asm) {
      if (asm.hasChanged()) {
        // Highlight the expression to give the user
        // some visual feedback on what was just
        // committed
        asm.root.dom().effect("highlight", {}, 1500);

        asm.set({
          sexp: asm.sexp()
        });
        asm.save({
          success: Notifications.raise('COMMIT_SUCCESS'),
        });
      }
    });
  },

  sexps: function () {
    return _.invoke(this._expressions, 'sexp');
  },

});

var Expression = Node.extend({
  _math: [],

  //Generates the array of strings which is compiled iff we
  //need to get a sexp.
  msexp: function () {
    var head = this.get('type');

    // Recursivly apply msexp on the children and flatten the
    // array
    if (!this.hasChildren()) {
      this._math = sexp(head, this.get('args'));
    } else {
      this._math = sexp(head, _.invoke(this.children, 'msexp'));
    }
    return this._math;
  },

  sexp: function () {
    this.msexp();
    return _.flatten(this._math).join(' ');
  },

  getCell: function () {
    return get_root(this).tree.cell;
  },

  toggleSelect: function () {
    if (this.get('selected') === true) {
      this.unselect();
    } else {
      this.select();
    }
  },

  unselect: function () {
    this.set({
      selected: false
    });
    Wise.Selection.remove(this);
    this.view.el.removeClass('selected');
  },

  select: function () {
    this.set({ selected: true });
    Wise.Selection.add(this);

    this.view.el.addClass('selected');
    this.selectionview = bt;

    // Move this to the Wise.Selection view handler
    var bt = new NodeSelectionView({
      model: this,
    }).render();

    placeholder_substitute();

  },

  register: function() {
    this.tree = this._parent.tree;

    if(this.hasChildren()) {
        for(child in this.children) {
            this.children[child].bind('struct_change',this.msexp);
            this.children[child].register();
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

//  url: function(){
//     return this.get('resource_uri') || this.collection.url;
//  }

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

///////////////////////////////////////////////////////////
// Construction Operations
///////////////////////////////////////////////////////////

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

function build_cell_from_json(json_input) {
  var cell_spec = json_input[0];
  var eqs_json = json_input[1];
  var asms_json = json_input[2];

  var new_cell = new Cell();

  new_cell.cid = cell_spec.cid;

  new_cell.set({
    id: cell_spec.id
  });

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

///////////////////////////////////////////////////////////
// Graft Operations
///////////////////////////////////////////////////////////

//       E  (Expression Tree)        F  ( Different Expression Tree)
//       |                           |
//      <A>                     →    X
//      / \                         / \
//     B   C                       Y   Z
//Build a tree from a json specifiction and then then graft (
//by replacement) onto a existing expression tree.

function graft_toplevel_from_json(old_node, json_input, transformation) {
  var cell = old_node.tree.cell;

  // cell index
  var old_index = old_node.tree.get('index');
  var newtree = build_tree_from_json(json_input);

//  newtree.root.transformed_by = transformation;
//  newtree.root.prev_state = old_node.sexp();

  old_node.swapNode(newtree.root);
  old_node.tree.root = newtree.root;
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


function graft_fragment_from_json(old_node, json_input, transformation) {

  if(!old_node) {
    throw 'Must specify which node to graft on top of';
  }

  if(!json_input) {
    throw 'Empty JSON passed to graft_fragment_from_json';
  }

  var treefrag = build_tree_from_json(json_input);

  //old_node.msexp();
  //treefrag.root.transformed_by = transformation;
  //treefrag.root.prev_state = old_node.sexp();

  // Associate new nodes with the active tree
  treefrag.root.tree = old_node.tree;

  old_node.swapNode(treefrag.root);

  return treefrag;
}

var graft_tree_from_json = graft_fragment_from_json;

///////////////////////////////////////////////////////////
// Misc
///////////////////////////////////////////////////////////

function sexp(head, args) {
  // Builds an array of the form (head arg[1] arg[2] ...)
  return _.flatten(['(', head, args, ')']);
}

function highlight_orphans() {
    Wise.Nodes.each(function(node) {
        if(node.tree === null) {
            $(node.view.el).css('background-color','red');
        }
    });
}

function check() {
    return shownode()._parent.children[shownode().index].cid == shownode().cid;
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