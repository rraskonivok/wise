$(document).ready(function() {

    module("Expression Trees");

    test("Dependencies", function() {

      equals(document, window.document,'Document loaded');
      ok($, 'jQuery exists');
      ok(Backbone, 'Backbone exists');
      ok(_, 'Underscore exists');
      ok(Wise, 'Wise exists');
      ok(Wise.Settings, 'Wise.Settings exists');

    });

    // cids assigned by Backbone are unique per session, and we
    // can use them to avoid the fact that jsDump fails for
    // circular references in the Node/Tree classes
    var eq = function(a, b, msg) {
        return ok(a.cid == b.cid, msg);
    };

    test("Construction", function() {

        // 0
        // |
        // 0
        var top = new Node();
        var tree = new RootedTree(top);
        ok(top, 'Constructed Node');
        ok(tree, 'Created Tree');

        ok(tree.root, 'tree has root');
        eq(tree.root, top, 'correct root node');

        equal(tree.root.hasChildren(), false, 'no children');
        ok(tree.root._parent,'has parent');
        deepEqual(tree.root.treeIndex(), [0], 'correct tree index'); 
        equal(tree.depth, 0, 'tree depth');
        equal(tree.count(), 1, 'tree count');

        //     O   
        //    / \  
        //   O   O 
        //   | 
        //   0
        var child1 = new Node(), 
            child2 = new Node(),
            child3 = new Node();

        raises(function() {
            child2.addNode(child3);
        },'attaching to orphan raises error');

        top.addNode(child1);
        top.addNode(child2);
        child1.addNode(child3);

        eq(child3.tree, tree,'tree is maintained');
        eq(child3._parent, child1,'subnodes');
        equal(tree.count(), 4, 'tree count');

        equal(child3.tree.root.cid, top.cid,'can access root');

    });

    test("Operations", function() {
    });

    test("Traversal", function() {
    });

});
