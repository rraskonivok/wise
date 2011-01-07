// The id of the Worksheet corresponding to its index in the
// database
var WORKSHEET_ID = 2;

// This is passed by Django to help us keep track of the #uid
// counter

// Count of how many "nodes"/uid tagged elements there are in the
// DOM
var NAMESPACE_INDEX = 3;

// Count of how many cells are in the workspace
var CELL_INDEX = 2;

// Raw json sent from the server when the page
// initializes
var JSON_TREE = $.parseJSON('[[{"index": 0, "eqs": ["cid0"], "assumptions": [], "id": 11, "cid": "cell0"}, [[{"toplevel": true, "children": ["cid1", "cid2"], "type": "Equation", "id": "cid0", "sid": 5}, {"toplevel": false, "args": ["x"], "type": "Variable", "id": "cid1", "children": []}, {"toplevel": false, "args": ["y"], "type": "Variable", "id": "cid2", "children": []}]], []], [{"index": 1, "eqs": [], "assumptions": [], "id": 12, "cid": "cell1"}, [], []]]');

// Lookup table of active equations which maps uid -> internal
// tree object
//var NODES = {};

// Array of cells, index corresponds to order on page. Each
// element contains another array of equations in that cell.
var CELLS = [];

var HAS_BROWSER = false;
