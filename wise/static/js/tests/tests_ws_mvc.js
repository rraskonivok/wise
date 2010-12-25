$(document).ready(function() {

    module("Worksheet MVC");

    // cids assigned by Backbone are unique per session, and we
    // can use them to avoid the fact that jsDump fails for
    // circular references in the Node/Tree classes
    var eq = function(a, b, msg) {
        return ok(a.cid == b.cid, msg);
    };

    test("JSON Serialization", function() {
        init();
        ok(Wise.Worksheet,'worksheet init');
        ok(Wise.Selection,'selection init');
        ok(Wise.Nodes,'nodes init');
        ok(Wise.Sidebar,'sidebar init');

        equal(Wise.Nodes.length,3,'corect # of nodes');
    });

    test("Worksheet Selection", function() {
        Wise.Nodes.invoke('select');
        equal(Wise.Selection.length, 3, 'selection success');
    });

});
