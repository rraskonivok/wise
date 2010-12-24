var WorksheetModel = Backbone.Collection.extend({
  url: '/ws',

//  url: function(){
//     return this.get('resource_uri') || this.collection.url;
//  }

  initialize: function () {
    this.url = '/ws/' + WORKSHEET_ID;
    this.id = WORKSHEET_ID;
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
    return $('#' + this.cid);
  },

  hasChildren: function () {
    return this.children.length > 0;
  },

  treeIndex: function () {
    if (this.get('toplevel')) {
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
  addNode: function (node) {
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
    //This is your standard tree graft
    newNode._parent = this._parent;
    newNode.index = this.index;
    newNode.depth = this.depth;
    newNode.tree = this.tree;
    newNode.toplevel = this.toplevel;

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

var Expression = Node.extend({
  _math: [],

  childrenChanged: function () {
    //        this.msexp();
    this.tree.set({
      sexp: this.tree.sexp()
    });
    this.tree._changed = true;
  },

  //Generates the array of strings which is compiled iff we
  //need to get a sexp.
  msexp: function () {
    var head = this.get('type')

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
    // If for some reason we don't have a sexp, then build it
    if(this._math.length == 0) { this.msexp(); }
    //TODO: REMOVE THIS!!!!!
    //this.msexp();
    return _.flatten(this._math).join(' ')
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

  }

});

