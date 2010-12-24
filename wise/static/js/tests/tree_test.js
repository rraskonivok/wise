$(document).ready(function() {

    module("Expression Trees");

    test("Sanity", function() {

      equals(document, window.document,'Document loaded');
      ok($, 'jQuery exists');
      ok(Backbone, 'Backbone exists');
      ok(_, 'Underscore exists');
      ok(Wise, 'Wise exists');
      ok(Wise.Settings, 'Wise.Settings exists');

    });


    test("Construction", function() {
        var top = new Node();
        var tree = new RootedTree(top);
        ok(top, 'Constructed Node');
        ok(tree, 'Created Tree');
        equal(tree.root.hasChildren(), false, 'no children');
        ok(tree.root._parent,'has parent');
        deepEqual(tree.root.treeIndex(), [0], 'correct tree index'); 
    });

});
