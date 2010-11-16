/*
Wise
Copyright (C) 2010 Stephen Diehl <sdiehl@clarku.edu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

///////////////////////////////////////////////////////////
// Initalization
///////////////////////////////////////////////////////////

var a = $.manageAjax.create('queue', {queue: true});

$(document).ajaxError(function() {
    error("Error connecting to server");
});

$(document).ready(function () {
    init();
});

$(document).ajaxStart(function () {
    $('#ajax_loading').show();
});

$(document).ajaxStop(function () {
    $('#ajax_loading').hide();
});

///////////////////////////////////////////////////////////
// Utilities
///////////////////////////////////////////////////////////

// Nerf the console.log function so that it doesn't accidently
// break if Firebug / JS Consle is turned off.

// Source: http://paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
  if(this.console){
    console.log( Array.prototype.slice.call(arguments) );
  }
};

// Begin Debuggin' Stuff
function showmath() {
   return selection.at(0).sexp();
}

function shownode() {
    if(selection.isEmpty()) {
        window.log('Select something idiot!');
    }
    return selection.at(0);
}

function rebuild_node() {
    //Shit went down, so rebuild the sexp
    //apply_transform('base/Rebuild',[selection.at(0)]);
    selection.at(0).msexp();
}

DISABLE_SIDEBAR = false;
// End Debuggin' Stuff

//----------------------
//Some JQuery Extensions
//----------------------
$.fn.exists = function () {
    return jQuery(this).length > 0;
}

$.fn.replace = function (htmls) {
    var replacer = $(htmls);
    $(this).replaceWith(replacer);
    return replacer;
};

$.fn.swap = function (b) {
    b = jQuery(b)[0];
    var a = this[0];

    var t = a.parentNode.insertBefore(document.createTextNode(''), a);
    b.parentNode.insertBefore(a, b);
    t.parentNode.insertBefore(b, t);
    t.parentNode.removeChild(t);

    return this;
};

//TODO: This is here for compatability reasons, move to fn.cid
$.fn.id = function () {
    return $(this).attr('id')
};

$.fn.cid = function () {
    return $(this).attr('id')
};

$.fn.is_toplevel = function() {
    return $(this).attr('toplevel') == 'true';
}

// Extract the id of an object and lookup its node
$.fn.node = function () {
    var node = NODES.getByCid($(this).id())
    if(!node) {
        error("The term you selected is 'broken', try refreshing its corresponding equation.");
        window.log($(this).id(),'not initalized in term db.');
        return;
    }
    return node;
};

$.fn.disableTextSelect = function () {
    return this.each(function () {
        if ($.browser.mozilla) { //Firefox
            $(this).css('MozUserSelect', 'none');
        } else if ($.browser.msie) { //IE
            $(this).bind('selectstart', function () {
                return false;
            });
        } else { //Opera, etc.
            (this).mousedown(function () {
                return false;
            });
        }
    });
};

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds) {
            break;
        }
    }
}

///////////////////////////////////////////////////////////
// Selection Handling
///////////////////////////////////////////////////////////

function add_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('add_to_both_sides', [root, node]);
    } else {
        error('Could not find toplevel expression');
    }
}

function sub_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('sub_from_both_sides', [root, node]);
    } else {
        error('Could not find toplevel expression');
    }
}

function mul_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('mul_both_sides', [root, node]);
    } else {
        error('Could not find toplevel expression');
    }
}

function div_shift() {
    var node = selection.at(0);
    var root = get_root(node);

    if(node && root) {
        apply_rule('div_both_sides', [root, node]);
    } else {
        error('Could not find toplevel expression');
    }
}

//Select the toplevel element
function select_parent(clear) {
    var start = selection.last();
    
    if(start.toplevel) {
        return;
    }

    if(clear) {
        base_mode();
    }

    select_term(get_parent(start));
}

function select_root(clear) {
    var start = selection.last();

    if(clear) {
        base_mode();
    }

    select_term(get_root(start));
}

function select_left_root(clear) {
    var start = selection.last();

    if(clear) {
        base_mode();
    }

    select_term(get_lhs(start)); 
}

function select_right_root(clear) {
    var start = selection.last();

    if(clear) {
        base_mode();
    }

    select_term(get_rhs(start)); 
}

function select_term(object) {

    hide_tooltips();

    $('#quasimode-indicator').fadeTo('fast',1);
    $('#basemode-indicator').fadeTo('fast',0.01);

    var clickedon = object.dom();

    var root = get_root(object);

    // If there is a active cell make it inactive
    if(active_cell) {
        active_cell.set({active: false});
    }

    cell = root.tree.cell;
    cell.set({active: true});

    // Shouldn't happen since select_term is induced by a jquery
    // binding on a DOM object, but we'll check anyways
    if(clickedon.length == 0) {
        window.log('DOM correspondance not found.');
        return;
    }

    if(selection.getByCid(object.cid) != null) {
        clickedon.removeClass('selected');
        selection.remove(object)
        object.set({selected: false});

    } else {
        object.set({selected: true});
        clickedon.addClass('selected');

        selection.add(object);

        var bt = new NodeSelectionView({
            model: object,
        });

        bt.render();

        $("#selectionlist").append(bt.el);

        active_cell = cell;
    }
    
    // If the object we just selected is not a placeholder then
    // go ahead and try chain substitution
    if (object.get('type') != 'Placeholder') {
        placeholder_substitute();
    }

    //if (selection.first().get('type') == 'Definition') {
    //    definition_apply();
    //}
}

substitute_stoplist = ['Placeholder'];

// ( Placeholder, Placeholder , ... , Expression )
function placeholder_substitute() {
    if (selection.length >= 2) {
//        heads = _.first(selection.list(), selection.count-1);
        var heads = selection.first(selection.length - 1);
        var last = selection.last();

        if(last.get('toplevel')) {
            error('Cannot substitute toplevel element into expression');
            return;
        }

        stream_of_phs = _.all(heads, 
            function(s) {
                return s.get('type') == 'Placeholder';
            }
        );

        if(stream_of_phs) {
            _.each(heads, function(slt) {
                apply_transform('base/PlaceholderSubstitute',[slt,last]);
            });
        }
    }
}

function definition_apply() {
    if (selection.count == 2) {
        fst = selection.nth(0);
        snd = selection.nth(1);

        if(fst.is_definition() && !snd.is_definition()) {
            apply_def(fst,[snd]);
        }
    }
}

// ( Definition, Definition , ... , Expression )

function format_selection() {
    $($("#selectionlist").children()).css('background-color', '#9CBD86');
    $($("#selectionlist").children()[0]).css('border', '2px solid #DD9090');
    $($("#selectionlist").children()[1]).css('border', '2px solid #989cd7');
}

///////////////////////////////////////////////////////////
// UI Handling
///////////////////////////////////////////////////////////


function error(text) {
    $.pnotify({
        'Error': 'Regular Notice',
        pnotify_text: text,
        pnotify_delay: 5000
    });
}

function notify(text) {
    $.pnotify({
        '': 'Regular Notice',
        pnotify_text: text,
        pnotify_delay: 5000
    });
}

function dialog(text) {
    $('#error_dialog').text(text);
    $('#error_dialog').dialog({
        modal: true,
        dialogClass: 'alert'
    });
}

function show_debug_menu() {
    $('#debug_menu').dialog();
    $('#horizslider').slider({
        slide: function (e, ui) {
            term_spacing(ui.value, null)
        }
    });
    $('#vertslider').slider({
        slide: function (e, ui) {
            term_spacing(null, ui.value)
        }
    });
}

function resize_parentheses() {

    var scaling_factor = 0.7;
    //Scale parentheses

    $('.pnths','#workspace').css({'fontSize':0});
    $('.pnths','#workspace').css({'height':0});

    //Pairs of parentheses
    ppairs = _.zip($('.left','#workspace'),$('.right','#workspace'));

    _.each(ppairs, function (obj) {
        parent_height = $(obj[0]).parent().height() * scaling_factor;
        //window.log(parent_height);
        if(parent_height > 50) {
            parent_height = 50;
        }
        $(obj[0]).css({'fontSize':String(parent_height) + 'px'});
        $(obj[1]).css({'fontSize':String(parent_height) + 'px'});
    });

    //TODO: replace $.each -> _.each
    $.each($('.sqrt-prefix','#workspace'), function (obj) {
        $(this).css({'height':0});
        parent_height = $(this).parent().height();
        $(this).css({'fontSize':String(parent_height) + 'px'});
    });
}

function term_spacing(x, y) {
    if (x) {
        $('.term').css('padding-right', x)
        $('.term').css('padding-left', x)
    }

    if (y) {
        $('.term').css('padding-top', y)
        $('.term').css('padding-bottom', y)
    }
}

function debug_math() {
    //TODO: Remove $.each
    $.each($('[math]'), function () {
        $(this).attr('title', $(this).attr('math'));
    });
}

function bind_hover_toggle() {
    $('#hovertoggle').toggle(

        // ---- On State ---
        function () {
            $('#workspace .term[math]').hover(

            function () {
//                $(this).fadeTo('slow',1);
//                $(this).addClass('term_hover');
//                $(this).dequeue();
            }, function () {
//                $(this).fadeTo('slow',0.3);
//                $(this).removeClass('term_hover');
//                $(this).dequeue();
            });

            $('#workspace .container[math]').hover(
                function () {
                    $(this).addClass('container_hover')
                    $(this).dequeue();
                }, function () {
                    $(this).removeClass('container_hover')
                    $(this).dequeue();
            });

        // ---- Off State ---
        }, function () {
            $('#workspace .term[math]').hover(

                function () {
                    $(this).removeClass('term_hover')
                })

                $('#workspace .container[math]').hover(
                    function () {
                        $(this).removeClass('container_hover')
                    }
                )
        })
}

///////////////////////////////////////////////////////////
// Server Queries
///////////////////////////////////////////////////////////

ajaxqueue = $.manageAjax.create('queue', {queue: false,
                                          preventDoubbleRequests: false,
                                          cacheResponse: true});

function heartbeat() {
    $.ajax({
      url: '/hb',
      dataType: 'html',
      type: 'GET',
      success: function(data) {
        if(!data) {
            error('Server is not responding.');
        }
      },
    }); 
}

function apply_rule(rule, operands) {
    var data = {};
    data.rule = rule;
    data.namespace_index = NAMESPACE_INDEX;

    // If nodes are not explicitely passed then use 
    // the workspace's current selection
    if (!operands) {
        if(selection.isEmpty()) {
            error("Selection is empty.");
            return;
        }

        //Fetch the math for each of the selections
        data.selections = selection.sexps();
        operands = selection.toArray();

    } else {
        data.selections = _.invoke(operands,'sexp');
    }

    $.post("/cmds/apply_rule/", data, function (response) {

        if (response.error) {
            error(response.error);
            base_mode();
            return;
        }

        NAMESPACE_INDEX = response.namespace_index;

        //Iterate over the elements in the image of the
        //transformation, attempt to map them 1:1 with the
        //elements in the domain. Elements mapped to 'null'
        //are deleted.
        for (var i = 0; i < response.new_html.length; i++) {
            obj = operands[i];

            //obj.queue(function() {
            //   $(this).fadeTo('slow',1);
            //   $(this).dequeue();
            //});

            if (response.new_html[i] == null) {
                obj.remove();
            }
            else if (response.new_html[i] == 'pass') {
                //console.log("Doing nothing");
            }
            else if (response.new_html[i] == 'delete') {
                //console.log("Deleting - at some point in the future");
            }
            else {
                toplevel = (response.new_json[i][0].toplevel)

                if (toplevel) {

                    graft_tree_from_json(
                        NODES.getByCid(obj.cid),
                        response.new_json[i],
                        data.rule
                    );

                    nsym = obj.dom().replace(response.new_html[i]).hide();
                    nsym.fadeIn('slow');
                    $('.equation button','#workspace').parent().buttonset();
                } else {

                    graft_tree_from_json(
                        NODES.getByCid(obj.cid), 
                        response.new_json[i],
                        data.rule
                    );

                    nsym = obj.dom().replace(response.new_html[i]).hide();
                    nsym.fadeIn('slow');
                }

                //Typeset any latex in the html the server just spit out
                mathjax_typeset($(nsym));
            }
        }

        base_mode();
        traverse_lines();
        resize_parentheses();
    }, "json");
}

function apply_def(def, selections) {
    var data = {};

    data.def = def.sexp()
    data.namespace_index = NAMESPACE_INDEX;

    if (selections == null) {

        //Fetch the math for each of the selections
        if(selection.count == 0) {
            error("Selection is empty.");
            return;
        }

        data.selections = selection.list_attr('math');

        if(data.selections.length == 1) {
            window.log('fading');
            selection.nth(0).queue(function() {
               $(this).fadeTo('slow',0.1);
               $(this).dequeue();
            });
        }

    }
    else {
        data.selections = _.invoke(selections,'math');
    }

    window.log(data);

    $.post("/cmds/apply_def/", data, function (data) {

        if (data.error) {
            error(data.error);
            base_mode();
            return;
        }

        //Iterate over the elements in the image of the
        //transformation, attempt to map them 1:1 with the
        //elements in the domain. Elements mapped to 'null'
        //are deleted.
        for (var i = 0; i < data.new_html.length; i++) {
            obj = selections[i];

            obj.queue(function() {
               $(this).fadeTo('slow',1);
               $(this).dequeue();
            });

            if (data.new_html[i] == null) {
                obj.remove();
            }
            else if (data.new_html[i] == 'pass') {
                //console.log("Doing nothing");
            }
            else if (data.new_html[i] == 'delete') {
                //console.log("Deleting - at some point in the future");
            }
            else {

                //changed this
                toplevel = (data.new_json[i][0].toplevel)

                if (toplevel) {
                    build_tree_from_json(data.new_json[i])

                    graft_tree_from_json(
                        NODES.getByCid(obj.id()), 
                        data.new_json[i],
                        'apply_def'
                    );

                    $('.equation button','#workspace').parent().buttonset();
                } else {

                    graft_tree_from_json(
                        NODES.getByCid(obj.id()), 
                        data.new_json[i],
                        'apply_def'
                    );

                }

                var nsym = obj.replace(data.new_html[i]).hide();
                nsym.fadeIn('slow');
                mathjax_typeset($(nsym));
            }
        }

        NAMESPACE_INDEX = data.namespace_index;

        base_mode();
        traverse_lines();
        resize_parentheses();
    }, "json");
}



function use_infix(code) {

    if(selection.isEmpty()) {
        error('No object selected');
        return;
    }

    selections = selection.toArray();

    postdata = {};
    postdata.namespace_index = NAMESPACE_INDEX;
    postdata.code = code;

    ajaxqueue.add({
        type: 'POST',
        async: 'false',
        url: "/cmds/use_infix/", 
        data: postdata, 
        datatype: 'json',
        success: function(data) {

            if (data.error) {
                error(data.error);
                base_mode();
                return;
            }

            if(!data.new_html) {
                error("Statement is not well-formed");
                $("#cmdinput").css('background-color','#D4A5A5');
                return;
            } else {
                hide_cmdline();
            }

            //Iterate over the elements in the image of the
            //transformation, attempt to map them 1:1 with the
            //elements in the domain. Elements mapped to 'null'
            //are deleted.
            for (var i = 0; i < data.new_html.length; i++) {
                obj = selections[i];

                if (data.new_html[i] == null) {
                    obj.remove();
                }
                else if (data.new_html[i] == 'pass') {
                    //console.log("Doing nothing");
                }
                else if (data.new_html[i] == 'delete') {
                    //console.log("Deleting - at some point in the future");
                }
                else {
                    toplevel = (data.new_json[i][0].toplevel)

                    if (toplevel) {
                        if(!obj.toplevel) {
                            error('Cannot replace toplevel node with non-toplevel node');
                        }

                        build_tree_from_json(data.new_json[i])

                        graft_tree_from_json(
                            NODES.getByCid(obj.cid),
                            data.new_json[i]
                        );

                        nsym = obj.dom().replace(data.new_html[i]);
                    } else {

                        graft_tree_from_json(
                            NODES.getByCid(obj.cid), 
                            data.new_json[i]
                        );

                        nsym = obj.dom().replace(data.new_html[i]);
                    }
                    //Typeset any latex in the html the server just spit out
                    mathjax_typeset($(nsym));
                }
            }

            NAMESPACE_INDEX = data.namespace_index;

            base_mode();
            traverse_lines();
            resize_parentheses();
        }});
}

function subs(obj) {
    if(selection.length > 0) {
        apply_transform('base/PlaceholderSubstitute',[selection.at(0), obj]);
    } else {
        error('Select an object to substitute into.');
    }
}

function apply_transform(transform, operands) {
    var postdata = {};
    postdata.transform = transform;
    postdata.namespace_index = NAMESPACE_INDEX;

    //if(operands.length == 1) {
    //    selections[0].fadeOut();
    //}

    if (!operands) {
        //Fetch the math for each of the selections
        if(selection.isEmpty()) {
            error("No selection to apply transform to");
            return;
        }
        // Get the sexps of the selected nodes
        postdata.selections = selection.sexps();
    } else {
        //TODO: change data.selections -> data.operands
        postdata.selections = _.map(operands, 
            function(obj) { 
                if(obj.constructor == String) {
                    return obj;
                } else {
                    return obj.sexp();
                } 
            }
        );
    }

    ajaxqueue.add({
        type: 'POST',
        async: 'false',
        url: "/cmds/apply_transform/", 
        data: postdata, 
        datatype: 'json',
        success: function(response) {

            if(!response) {
                error('Server side error in processing apply_transform.');
                return;
            }

            if (response.error) {
                error(response.error);
                base_mode();
                return
            }

            //Iterate over the elements in the image of the
            //transformation, attempt to map them 1:1 with the
            //elements in the domain. Elements mapped to 'null'
            //are deleted.
            for (var i = 0; i < response.new_html.length; i++) {
                obj = operands[i];

                if (response.new_html[i] == null) {
                    obj.remove();
                }
                else if (response.new_html[i] == 'pass') {
                    //console.log("Doing nothing");
                }
                else if (response.new_html[i] == 'delete') {
                    //console.log("Deleting - at some point in the future");
                }
                else {
                    var toplevel = (response.new_json[i][0].toplevel);
                    if (toplevel) {
                        build_tree_from_json(response.new_json[i]);

                        graft_tree_from_json(
                            NODES.getByCid(obj.cid),
                            response.new_json[i],
                            postdata.transform
                        );

                        nsym = obj.dom().replace(response.new_html[i]);
                    } else {

                        graft_tree_from_json(
                            NODES.getByCid(obj.cid), 
                            response.new_json[i],
                            postdata.transform
                        );
                        nsym = obj.dom().replace(response.new_html[i]);
                    }

                    mathjax_typeset($(nsym));
                }
            }

            NAMESPACE_INDEX = response.namespace_index;

            base_mode();
            traverse_lines();
            resize_parentheses();
        }});
}

function new_line(type, index) {
    var data = {};
    data.namespace_index = NAMESPACE_INDEX;
    data.cell_index = CELL_INDEX;
    data.type = type;

    if(index != undefined) {
        active_cell = WORKSHEET.getByCid(index);
    }

    if(!active_cell) {
        error("Select a cell to insert into");
        return;
    }

    $.post("/cmds/new_line/", data, function (data) {

        if (data.error) {
            error(data.error);
        }

        if (data.new_html) {

            new_cell_html = $(data.new_html);
            active_cell.dom().append(new_cell_html);
            mathjax_typeset(new_cell_html);
            traverse_lines();

            var eq = build_tree_from_json(data.new_json);

            eq.cell = active_cell;
            eq.set({cell: active_cell.id});

            active_cell.addExpression(eq);

        }

        NAMESPACE_INDEX = data.namespace_index;
        $('.equation button','#workspace').parent().buttonset();
    }, 'json')
}

function new_cell() {
    data = {};
    data.namespace_index = NAMESPACE_INDEX;
    data.cell_index = CELL_INDEX;

    $.post("/cmds/new_cell/", data, function (response) {

        if (response.error) {
            error(response.error);
        }

        if (response.new_html) {

            new_cell_html = $(response.new_html);
            $("#workspace").append(new_cell_html);
            mathjax_typeset(new_cell_html);
            traverse_lines();

            var new_cell = build_cell_from_json(response.new_json);
            new_cell_html.attr('id',new_cell.cid);

            active_cell = new_cell;

            WORKSHEET.add(new_cell);
            CELL_INDEX = response.cell_index;
            NAMESPACE_INDEX = response.namespace_index;
            $('.equation button','#workspace').parent().buttonset();

            var cs = new CellSelection({
                model: new_cell,
            });
            cs.render();

            $('#cell_selection').append(cs.el);
            //new_cell.set({active: true});
        }
    });
}

function save_workspace() {
    data = {};
    i = 0;

    //TODO: Remove $.each
    $.each($("tr[toplevel='true']", '#workspace'), function (obj) {
        data[i] = [$(this).attr('math'), $(this).find('.annotation').text(), $(this).attr('data-confluent'), $(this).attr('data-public')];
        i += 1;
    });

    //Flash the border to indicate we've saved.
    $('#workspace').animate({
        border: "5px solid red"
    }, 300);
    $('#workspace').animate({
        border: "0px solid black"
    }, 300);

    console.log(data);

    $.post("save/", data, function (data) {
        if (data.error) {
            error(data.error);
        }
        if (data.success) {
            error('Save succesfull.')
        }
    }, 'json')
}


///////////////////////////////////////////////////////////
// Tree Traversal
///////////////////////////////////////////////////////////

function traverse_lines() {
    // jQuery tooltip croaks if we apply $.tooltip multiple times
    // so we just ignore elements that we've already initiated
//    untooltiped = _.reject($('[math-type]','#workspace'), function(obj){ return obj.tooltipText });

    unselectable = _.reject($('[math-meta-class=term]','#workspace'), function(obj){ return obj.selectable });
    
    function make_selectable(obj) {
        $(obj).click(function(event) {
            // Take the id of the DOM object clicked on and match it to a expression Node
            var node = NODES.getByCid($(this).id());
            select_term(node);
            // stopPropogation prevents stacked elements from being selected at the same time
            event.stopPropagation();
        });
        // Pass this object in subsequent interations
        obj.selectable = true;
    };

    _.each(unselectable, make_selectable);

    //unselectable = _.reject($('[math-meta-class=term]:not(.placeholder)','#math_palette'), function(obj){ return obj.selectable });
    //_.each(unselectable, make_selectable);

    resize_parentheses();

    //_.map($('span[title]'),make_tooltips);
}

///////////////////////////////////////////////////////////
// Drag & Drop
///////////////////////////////////////////////////////////

function make_sortable(object, connector, options) {
    var group_id = $(object).attr('id');
    $(object).sortable(options);
}

///////////////////////////////////////////////////////////
// Math Parsing & Generating
///////////////////////////////////////////////////////////

function check_container(object) {

    //TODO: The original algorithm I wrote many moons ago seems
    //to break if we have strange <script> tags inside the
    //container. So just remove them... until I fix it.
  
    $('[type=math/tex; mode=display]',object).remove();
    // This handles stupid expression checking that is too expensive 
    // to do via Ajax, ie removing infix sugar 
    _.each(object.children(':not(script)'), function () {
        var prev = $(this).prev();
        var cur = $(this);
        var next = $(this).next();
        var last = $(object).children(':last-child');
        var first = $(object).children(':first-child');
        var group = $(this).attr('group');
        if (group != "") {

            // -- Rules for handling parenthesis --
            //This forces left parenthesis over to the left
            if (cur.hasClass('term') && next.hasClass('pnths') && next.hasClass('left')) {
                cur.swap(next);
            }

            //This forces left parenthesis over to the left
            if (cur.hasClass('pnths') && next.hasClass('term') && cur.hasClass('right')) {
                cur.swap(next);
            }

            // -- Rules for cleaning up infix sugar --
            group_type = $('#' + group).attr('math-type');

            //  A + + B  --> A  + B
            if (cur.hasClass('infix') && next.hasClass('infix')) {
                cur.remove();
            }

            // A + - B  --> A - B
            if (cur.hasClass('infix') && next.attr('math-type') == 'Negate') {
                cur.remove();
            }

            //  ( + A  --> ( A
            if (cur.hasClass('pnths') && next.hasClass('infix')) {
                next.remove();
            }

            //  + ) --> )
            if (cur.hasClass('infix') && next.hasClass('pnths')) {
                cur.remove();
            }

            // + A + B --> A + B
            if (first.hasClass('infix')) {
                first.remove();
            }

            // A + B + --> A + B
            if (last.hasClass('infix')) {
                last.remove();
            }

        }
    });
}

function check_combinations(object) {
    //Check to see if two terms are explicitly dragged next to each other and 
    //query the server to see if we can combine them into something
    if ($(object).attr('locked') == 'true') {
        return
    }
    //TODO: Remove $.each
    $.each(object.children(), function () {
        prev = $(this).prev();
        cur = $(this);
        next = $(this).next();
        group = $(this).attr('group');
        if (group != "") {
            group_type = $('#' + group).attr('math-type');

            // A + B C + D -> A + combine(B,C) + D
            if (cur.attr('math-meta-class') == 'term' && next.attr('math-meta-class') == 'term') {
                //The one exception (i.e. filthy hack) is that
                //dragging a negated term next to any other
                //doesn't induce the combine command since the
                //negation sign on the negated term pretends
                //it is sugar, long story short it looks
                //prettier
                if (next.attr('math-type') != 'Negate') {
                    combine(cur, next, group_type);
                    check_container(object)
                }
            }
        }
    });
}

function toggle_confluence(obj) {
    if (obj.attr('data-confluent') == 0) {
        obj.attr('data-confluent', 1)
        obj.find('.confluence').addClass('ui-icon-bullet')
        obj.find('.confluence').removeClass('ui-icon-radio-off')
    } else {
        obj.attr('data-confluent', 0)
        obj.find('.confluence').addClass('ui-icon-radio-off')
        obj.find('.confluence').removeClass('ui-icon-bullet')
    }
}

function mathjax_typeset(element) {
    //if(DISABLE_TYPESETTING) {
    //    return;
    //}

    //Refresh math for a specific element
    if (element) {
        MathJax.Hub.Queue(["Typeset",MathJax.Hub,element[0]]);
        MathJax.Hub.Queue(
            function () {
 //               element.css('visibility', 'visible')
            }
        );
    }
    //Refresh math Globally, shouldn't be called too much because
    //it bogs down the browser
    else {
        console.log('Refreshing all math on the page');
        MathJax.Hub.Process();
        //jsMath.ConvertTeX()
        //jsMath.ProcessBeforeShowing()
    }
}

function select_equation(id) {
    select_term(NODES.getByCid(id));  
}

function select_lhs(id) {
    select_term(NODES.getByCid(id).children[0].children[0]);
}

function select_rhs(id) {
    select_term(NODES.getByCid(id).children[1].children[0]);  
}

function next_placeholder(start) {
    last = $('.lines .placeholder:last')
    first = $('.lines .placeholder:first')

    if (!start) {
        if (selection.nth(0).exists()) {
            start = selection.nth(0)
        }
        else {
            start = first
        }
    }


    if ($(last).attr('id') == $(start).attr('id')) {
        base_mode();
        select_term(first)
        return
    }

    placeholders = $('.lines .placeholder')

    var i = 0;
    for (i = 0; i <= placeholders.length; i++) {
        if ($(placeholders[i]).attr('id') == $(start).attr('id')) {
            if (i === placeholders.length) {
                select_term($(placeholders[1]))
            }
            else {
                select_term($(placeholders[i + 1]))
            }
        }
    }
    base_mode();
}

function remove_element() {
    if(selection.isEmpty()) {
        error('Selection is empty.');
        return;
    }

    //$( "#dialog-ask" ).dialog({
    //    closeOnEscape: true,
    //    modal: true,
    //    resizable: false,
    //    buttons: {
    //        Ok: function() {
    //            $( this ).dialog( "close" );
    //        }
    //    }
    //}); 

    selection.each(function(elem) {

        if(elem.get('toplevel')) {
            elem.dom().remove();
            elem.delNode();
        } else {
            apply_transform('base/Delete', [elem]);
        }

    });
}

var ctrlPressed = false;

$(window).keydown(function(evt) {
  if (evt.which == 17) { // ctrl
    ctrlPressed = true;
  }
}).keyup(function(evt) {
  if (evt.which == 17) { // ctrl
    ctrlPressed = false;
  }
});

$('.container','#workspace').live('mouseover mouseout', function(e) {
  ths = $(this);
  if (e.type == 'mouseover' && ctrlPressed) {
            ths.css('padding-left','10px');
            ths.css('padding-right','10px');
            ths.addClass('preselect');
  } else {
            ths.css('padding','inherit');
            ths.removeClass('preselect');
  }
});

///////////////////////////////////////////////////////////
// Palette Loading / Handeling
///////////////////////////////////////////////////////////

function load_rules_palette() {
    if(DISABLE_SIDEBAR) {
        return;
    }

    $.ajax({
            url: '/rule_request',
            success: function(data) {
                $("#rules_palette").replace(data);
                $(".panel_category","#rules_palette").bind('click',function() {
                        $(this).next().toggle();
                        // Only typeset when needed
                        MathJax.Hub.Typeset($(this).next()[0]);
                        return false
                }).next().hide();

            }
    });
}

function load_math_palette() {
    if(DISABLE_SIDEBAR) {
        return;
    }

    $.ajax({
        url: '/palette/',
        success: function(data) {
            $("#math_palette").replace(data)
    
            //Make the palette sections collapsable
            $(".panel_category","#math_palette").bind('click',function() {
                    $(this).next().toggle();
                    _.map($(this).next(), make_buttons_uniform);
                    return false;
            }).next().hide();

            //Typeset the panel
            MathJax.Hub.Typeset($(this).next()[0]);
    
            //Make the math terms interactive
            traverse_lines();
            resize_parentheses()
            $("#math_palette").resizable({ handles: 's' });
        }
    });

}

//Stupid function to make buttons in each panel have the same height
function make_buttons_uniform(obj) {
    //var heights = [];
    //buttons = $(obj).find('button');

    //_.each(buttons, function(btn) {
    //    heights.push($(btn).height()); 
    //});

    //var max = _.max(heights);
    //if(max != 0) {
    //    _.each(buttons, function(btn) {
    //        $(btn).height(max + 5); 
    //        $(btn).width($(btn).width() + 5); 
    //    });
    //}
}

function palette(num) {
    if(num == 1) {
        $('#math_palette').show();
        $('#rules_palette').hide();
        $('#tab_math_palette').addClass('active');
        $('#tab_rules_palette').removeClass('active');
    }
    else {
        $('#math_palette').hide();
        $('#rules_palette').show();
        $('#tab_rules_palette').addClass('active');
        $('#tab_math_palette').removeClass('active');
    }
}


///////////////////////////////////////////////////////////
// Command Line
///////////////////////////////////////////////////////////

$('#cmdline').submit(function() {
    use_infix($("#cmdinput").val());
    $("#cmdinput").blur();
    return false;
});

///////////////////////////////////////////////////////////
// Initialize the Term DB
///////////////////////////////////////////////////////////

// Takes the inital JSON that Django injects into the page
// and calls build_tree_from_json to initialize the term
// database

function init_nodes() {
    NODES     = new Backbone.Collection();
    WORKSHEET = new Worksheet();

    _.each(JSON_TREE, function(cell_json) {
        var new_cell = build_cell_from_json(cell_json);
        WORKSHEET.add(new_cell);

        var cs = new CellSelection({
            model: new_cell,
        });
        cs.render();

        $('#cell_selection').append(cs.el);
    });

    // Make the new elements selectable
    traverse_lines();
}
