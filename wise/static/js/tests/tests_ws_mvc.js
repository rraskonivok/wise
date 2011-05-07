$(document).ready(function() {

    require('init').init();

    module("Worksheet MVC");

    // cids assigned by Backbone are unique per session, and we
    // can use them to avoid the fact that jsDump fails for
    // circular references in the Node/Tree classes
    var eq = function(a, b, msg) {
        return ok(a.cid == b.cid, msg);
    };

    test("Worksheet Init", function() {
        ok(Wise,'base application exists');
        ok(Wise.Worksheet,'worksheet init');
        ok(Wise.Selection,'selection init');
        ok(Wise.Nodes,'nodes init');
        ok(Wise.Sidebar,'sidebar init');

        equal(Wise.Nodes.length,3,'corect # of nodes');
    });

    test("Worksheet Selection", function() {
        Wise.Nodes.invoke('select');
        equal(Wise.Selection.length, 3, 'selection success');
        ok(Wise.Selection.at(0));

        equal(Wise.Selection.at(0).tree.sexp(), "( Equation ( Variable x ) ( Variable y ) )", 'sexp generation ok');
        equal(Wise.Selection.at(0).tree.root.sexp(), "( Equation ( Variable x ) ( Variable y ) )", 'sexp generation ok');
        equal(Wise.Selection.at(0).tree.root.children[0].sexp(), '( Variable x )', 'sexp generation ok');
        equal(Wise.Selection.at(0).tree.root.children[1].sexp(), '( Variable y )', 'sexp generatin ok');

        Wise.Selection.at(1).unselect();
        equal(Wise.Selection.length, 2, 'unselect success');

    });

    //TODO: use mockjax so we don't have to depend on the server
    //test("Worksheet Rules", function() {
    //    Wise.Selection.clear();
    //    // ( Equation ... 
    //    var el1 = Wise.Nodes.at(0);
    //    // ( Variable x)
    //    var el2 = Wise.Nodes.at(1);

    //    // Wait for ajax request
    //    stop(2000);

    //    apply_rule('eq_add',[el1, el2], function() {
    //        equal(NAMESPACE_INDEX, 10, 'namespace incremented after ajax');
    //        start();
    //    });

    //});



});
