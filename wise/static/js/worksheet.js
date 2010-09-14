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

//Optimization Tips:
//http://net.tutsplus.com/tutorials/javascript-ajax/10-ways-to-instantly-increase-your-jquery-performance/
//http://www.codenothing.com/archives/2010/8-jquery-micro-optimization-tips/

///////////////////////////////////////////////////////////
// Utilities
///////////////////////////////////////////////////////////

// Nerf the console.log function so that it doesn't accidently
// break if Firebug / JS Consle is turned off.

// Source: http://paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
//
window.log = function(){
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
  if(this.console){
    console.log( Array.prototype.slice.call(arguments) );
  }
};

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

$.fn.id = function () {
    return $(this).attr('id')
};

$.fn.math = function () {
    return $(this).attr('math')
};

$.fn.group = function () {
    return $(this).attr('group')
};

$.fn.mathtype = function () {
    return $(this).attr('math-type')
};

$.fn.is_placeholder = function() {
    return $(this).attr('math-type') == 'Placeholder';
}

$.fn.is_toplevel = function() {
    return $(this).attr('toplevel') == 'true';
}

$.fn.node = function () {
    return NODES[$(this).id()]
};

$.extend($.fn.disableTextSelect = function () {
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
});

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

// Out global selection container
var selection = {};
selection.count = 0;
selection.objs = {};
selection.__lst = [];

//For future reference Chrom(ium) and Firefox handle insertion by
//differently. Firefox (sanely) just pushes new elements at the
//end of the hash table while Chromium presorts them. This is an
//issue since we need them to be ordered for when we build __lst.
//Fix this at some point.
selection.add = function (obj) {
    this.objs[obj.id()] = obj;
    this.count += 1;
}

selection.del = function (key) {
    delete this.objs[key]
    this.count -= 1;
}

selection.get = function (key) {
    return this.objs[key];
}

selection.list = function () {
    var lst = [];
    for (i in this.objs) {
        lst.push(this.objs[i]);
    }
    this.__lst = lst;
    return lst;
}

//Return a list of the given attribute of the elements
//Ex: selection.list_attr('math')
selection.list_attr = function (prop) {
    var lst = [];
    for (i in this.objs) {
        lst.push(this.objs[i].attr(prop));
    }
    return lst;
}

selection.nth = function (n) {
    if (this.__lst.length == 0) {
        this.list();
    }
    this.list();
    var nth = this.__lst[n];

    //We do this so that selection.nth(0).exists will return
    //false if the value is not in the array
    if (nth == undefined) {
        return $();
    } else {
        return nth;
    }
}

selection.clear = function () {
    this.objs = {};
    this.__lst = [];
    this.count = 0;
}

function clear_selection() {
    // Clear the selection indicator bar
    $("#selectionlist").empty();

    // Clear the selection highlighting in the workspace
    $('.selected').removeClass('selected');

    selection.clear();
}

substitute_stoplist = ['Placeholder'];

function select_term(object) {
    //Since the selections have changed clear any looked-up (is that even a word?) actions
    clear_lookups();

    clickedon = $(object);

    //We shouldn't be able to click on the "invisible" addition
    //container we add to each of the RHS or LHS
    container = get_container(clickedon);

    if (container != undefined) {
        if (container.attr('math-type') == 'RHS' || container.attr('math-type') == 'LHS') {
            return
        }
    }

    if (clickedon.hasClass('selected')) {
        clickedon.removeClass('selected');
        id = clickedon.attr("id");
        //TODO: Remove $.each
        $.each($("#selectionlist button"), function () {
            if ($(this).attr('index') === id) {
                $(this).remove();
            }
        });
        selection.del(id)
    }
    else {
        clickedon.addClass('selected');
        typ = clickedon.attr('math-type');
        li = $(document.createElement('button')).html(typ)
        li.button()

        cancel = $(document.createElement('div'))
        cancel.addClass('ui-icon')
        cancel.addClass('ui-icon-close')
        cancel.css('float', 'left')
        cancel.css('cursor', 'pointer')

        li.prepend(cancel)
        index = clickedon.attr('id')

        selection.add(clickedon);

        li.attr('index', index)

        cancel.attr('index', index)

        li.bind('mouseover', function () {
            index = $(this).attr('index')
            obj = selection.get(index)
            obj.css('background', '#DD9090');
        });
        li.bind('mouseout', function () {
            index = $(this).attr('index')
            obj = selection.get(index)
            obj.css('background', 'inherit');
        });
        li.bind('click', function () {
            index = $(this).attr('index')

            obj = selection.get(index)
            obj.removeClass('selected');
            obj.css('background', 'inherit');

            selection.del(index)

            $(this).remove()
            format_selection()
        });

        $("#selectionlist").append(li);

        format_selection();
    }
    
    if (clickedon.mathtype() != 'Placeholder') {
        placeholder_substitute();
    }
}

function placeholder_substitute() {
    if (selection.count >= 2) {
        heads = _.first(selection.list(), selection.count-1);
        last = _.last(selection.list());

        if(last.is_toplevel()) {
            error('Cannot substitute toplevel element into expression');
            return;
        }

        //Yah, this hoses Chromium unless we add == true at
        //the end, don't understand why
        run_of_ph = ( _.all(_.invoke(heads,'is_placeholder')) == true );

        if(run_of_ph == true) {
            _.each(heads, function(slt) {
                apply_transform('base/PlaceholderSubstitute',[slt,last]);
            });
        }
    }
}

function format_selection() {
    $($("#selectionlist").children()).css('background-color', '#9CBD86');
    $($("#selectionlist").children()[0]).css('border', '2px solid #DD9090');
    $($("#selectionlist").children()[1]).css('border', '2px solid #989cd7');
}

///////////////////////////////////////////////////////////
// UI Handling
///////////////////////////////////////////////////////////
$(document).ajaxStart(function () {
    $('#ajax_loading').show()
})
$(document).ajaxStop(function () {
    $('#ajax_loading').hide()
})

function error(text) {
    $.pnotify({
        'Error': 'Regular Notice',
        pnotify_text: text,
        pnotify_delay: 5000
    });
    //$('#error_dialog').text(text);
    //$('#error_dialog').dialog({modal:true,dialogClass:'alert'});
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

function clear_lookups() {
    $('#options').fadeOut()
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
    //Scale parentheses
    //TODO: Remove $.each
    $.each($('.pnths','#workspace'), function (obj) {
        parent_height = $(this).parent().height();
        $(this).height(parent_height)
        $(this).css('margin-top', -parent_height / 3)
        $(this).css('font-size', String(parent_height / 3) + 'px')
    });
}

function fade_and_destroy(object) {
    $(object).fadeOut('fast', function () {
        $(object).remove();
    });
}

function fade_old_new(old, news) {
    $(old).hide('slow', function () {
        $(news).show(function () {
            $(old).remove();
        });
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

function cleanup_ajax_scripts() {
    //The ensures that any <script> tags inserted via ajax don't get executed more than once
    $("script[data-type=ajax]").remove()
}

function debug_math() {
    //TODO: Remove $.each
    $.each($('[math]'), function () {
        $(this).attr('title', $(this).attr('math'));
    });
}

function highlight() {

}

function bind_hover_toggle() {
    $('#hovertoggle').toggle(

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
            })

            $('#workspace .container[math]').hover(

            function () {
                $(this).addClass('container_hover')
                $(this).dequeue();
            }, function () {
                $(this).removeClass('container_hover')
                $(this).dequeue();
            })

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

function toggle_sageinput() {
    $('#sage_input').dialog();
}

function show_cmd() {
    if (selection.count > 0) {
        $('#cmd_input').toggle();
        $("#sage_cmd").focus()
    }
}

function exec_cmd() {
    sage_inline($('#sage_cmd').val())
}

function debug_colors(object) {
    $('li[math-meta-class=term]').css('border-bottom', '5px solid red');
    $('ul[math-type]').css('border-bottom', '5px solid blue');
    $('.rhs').css('border-bottom', 'none');
    $('.lhs').css('border-bottom', 'none');
    $('.equation').css('background-color', '#CCCCCC');
    $('.rhs').css('background-color', '#FFCCCC');
    $('.lhs').css('background-color', '#CCFF00');
}

///////////////////////////////////////////////////////////
// Server Queries
///////////////////////////////////////////////////////////

function lookup_transform() {
    data = {}

    //Get the types of the values we have selected
    data.selections = selection.list_attr('math-type')

    //Iterate through all elements
    //if(get_nested(first,second) != null)
    //{
    //    data.nested = true
    //}
    //else
    //{
    //    data.nested = false
    //}
    //context = get_common_context(first,second)
    //if(context != null)
    //{
    //    context = context.attr('math-type') 
    //}
    //data.context = context
    $.post("/cmds/lookup_transform/", data, function (data) {
        if (data.empty) {
            notify('No transforms found for given objects');
            return;
        }

        //Generate buttons which invoke the transformations
        $('#options').empty();

        for (var mapping in data) {
            var pretty = data[mapping][0]
            var internal = data[mapping][1]
            button = $(document.createElement('button')).html(pretty)
            button.attr('internal', internal)

            button.bind('click', function () {
                apply_transform($(this).attr('internal'))
            })

//            $('#selectionlist').hide();
            $('#options').prepend(button);
            $('#options').show();
            $('#options button').button();
        }
    }, 'json')
}

function apply_rule(rule, selections) {
    var data = {}
    data.rule = rule
    data.namespace_index = NAMESPACE_INDEX;

    if (selections == null) {
        //Fetch the math for each of the selections
        if(selection.count == 0) {
            error("Selection is empty.");
            return;
        }
        data.selections = selection.list_attr('math')
    }
    else {
        data.selections = selections
    }

    $.post("/cmds/apply_rule/", data, function (data) {

        if (data.error) {
            error(data.error)
            clear_selection()
            return
        }

        //Iterate over the elements in the image of the
        //transformation, attempt to map them 1:1 with the
        //elements in the domain. Elements mapped to 'null'
        //are deleted.
        for (var i = 0; i < data.new_html.length; i++) {
            obj = selection.nth(i)
            group_id = obj.attr('group');
            group_id_cache = String(group_id)
            obj.fadeOut('slow');

            if (data.new_html[i] == null) {
                obj.remove();
            }
            else if (data.new_html[i] == 'pass') {
                //onsole.log("Doing nothing");
            }
            else if (data.new_html[i] == 'delete') {
                //console.log("Deleting - at some point in the future");
            }
            else {
                toplevel = (data.new_json[i][0].type)
                if (toplevel == 'Definition' | toplevel == 'Equation') {
                    build_tree_from_json(data.new_json[i])
                    //merge_json_to_tree(NODES[obj.id()],data.new_json[i]);
                    nsym = obj.replace(data.new_html[i]).hide();
                    //nsym.attr('group',group_id_cache);
                    refresh_jsmath($(nsym));
                    nsym.fadeIn('slow');
                    $('.equation button','#workspace').parent().buttonset();
                } else {
                    merge_json_to_tree(NODES[obj.id()], data.new_json[i]);
                    nsym = obj.replace(data.new_html[i]).hide();
                    nsym.attr('group', group_id_cache);
                    refresh_jsmath($(nsym))
                    nsym.fadeIn('slow');
                }
                update(get_container(nsym))
                //Check to see if the uid assigning failed
                if (nsym.find('#None').length > 0) {
                    error("Warning: some elements do not have uids");
                }
                if (nsym.find('[group="None"]').length > 0) {
                    error("Warning: orphaned elements");
                }
            }
        }

        NAMESPACE_INDEX = data.namespace_index;

        clear_selection()
        traverse_lines();
        //update(get_container(obj))
    }, "json");

    cleanup_ajax_scripts()
    clear_lookups()
}

function apply_transform(transform, selections) {
    var data = {}
    data.transform = transform
    data.namespace_index = NAMESPACE_INDEX;

    if (selections == null) {
        //Fetch the math for each of the selections
        if(selection.count == 0) {
            error("No selection to apply transform to");
            return;
        }
        selections = selections.list();
        data.selections = selection.list_attr('math')
    }
    else {
        data.selections = _.invoke(selections,'math');
    }

    $.post("/cmds/apply_transform/", data, function (data) {

        if (data.error) {
            error(data.error)
            clear_selection()
            return
        }

        //Iterate over the elements in the image of the
        //transformation, attempt to map them 1:1 with the
        //elements in the domain. Elements mapped to 'null'
        //are deleted.
        for (var i = 0; i < data.new_html.length; i++) {
            obj = selections[i];
            group_id = obj.attr('group');
            group_id_cache = String(group_id)

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
                toplevel = (data.new_json[i][0].type)
                if (toplevel == 'Definition' | toplevel == 'Equation') {
                    build_tree_from_json(data.new_json[i])
                    //merge_json_to_tree(NODES[obj.id()],data.new_json[i]);
                    nsym = obj.replace(data.new_html[i]);
                    //nsym.attr('group',group_id_cache);
                    refresh_jsmath($(nsym))
                } else {
                    merge_json_to_tree(NODES[obj.id()], data.new_json[i]);
                    nsym = obj.replace(data.new_html[i]);
                    nsym.attr('group', group_id_cache);
                    refresh_jsmath($(nsym))
                }
                update(get_container(nsym))
                //Check to see if the uid assigning failed
                if (nsym.find('#None').length > 0) {
                    error("Warning: some elements do not have uids");
                }
            }
        }

        NAMESPACE_INDEX = data.namespace_index;

        clear_selection()
        traverse_lines();
        //update(get_container(obj))
    }, "json");

    cleanup_ajax_scripts()
    clear_lookups()
}

function receive(ui, receiver, group_id) {
    group_id = receiver.attr('id')

    obj = ui.item
    //If we drop an element in make sure we associate it with the group immediately
    obj.attr('group', group_id);

    //If we drag from a jquery draggable then the ui.item doesn't exist here yet
    //so just remap all the children with the group... this should be safe (right?)
    receiver.children('[math]').attr('group', group_id)

    //Make sure nothing is changed while we process the request
    receiver.attr('locked', 'true')

    data = {
        //The math of the dragged object 
        obj: ui.item.attr('math'),
        obj_type: ui.item.attr('math-type'),

        //The math of the receiving object
        receiver: receiver.attr('math'),
        receiver_type: receiver.attr('math-type'),
        receiver_context: get_container(receiver).attr('math-type'),

        //The math of the sender objec
        sender: ui.sender.attr('math'),
        sender_type: ui.sender.attr('math-type'),
        sender_context: get_container(ui.sender).attr('math-type'),

        //The new position of the dragged obect inside receiver
        new_position: ui.item.parent().children("[math]").index(ui.item),

        namespace_index: NAMESPACE_INDEX
    }

    $.post("/cmds/receive/", data, function (data) {

        if (data.error) {
            error(data.error);
            return
        }

        nsym = obj.replace(data.new_html);
        nsym.attr('group', group_id);

        refresh_jsmath($(nsym));
        receiver.attr('locked', 'false');

        update(get_container(nsym))

        //append_json_to_tree(NODES[receiver.id()],data.new_json);
        append_to_tree(NODES[receiver.id()], data.new_json);

        //Remove the old element from the tree
        NODES[obj.id()].delNode();

        NAMESPACE_INDEX = data.namespace_index;
    }, "json");

    cleanup_ajax_scripts();
}

function remove(ui, removed) {
    //Rather unintuitivly this handles transformations that are
    //induced after a object is removed from a container. The
    //best example is when the last element from a equation side
    //(i.e. LHS) is removed, this induces the remove method on
    //LHS and appends a zero.
    group_id = removed.attr('id')
    obj = ui.item
    removed.attr('locked', 'true')

    data = {
        //The math of the dragged object 
        obj: ui.item.attr('math'),
        obj_type: ui.item.attr('math-type'),

        //The math of the sender object
        sender: removed.attr('math'),
        sender_type: removed.attr('math-type'),
        sender_context: get_container(removed).attr('math-type'),

        namespace_index: NAMESPACE_INDEX
    }

    $.post("/cmds/remove/", data, function (data) {
        if (data.error) {
            error(data.error)
            return
        }

        if (data.new_html) {
            nsym = $(data.new_html).appendTo(removed);
            nsym.attr('group', group_id);

            refresh_jsmath(nsym);
            append_to_tree(NODES[removed.id()], data.new_json);

            removed.attr('locked', 'false')
            update_math(removed);
            NAMESPACE_INDEX = data.namespace_index;
        }
    }, "json");
    cleanup_ajax_scripts()
}

function combine(first, second, context) {
    data = {};
    data.context = context
    data.first = $(first).attr('math');
    data.second = $(second).attr('math');
    data.namespace_index = NAMESPACE_INDEX;

    if ($(first).attr('group') != $(second).attr('group')) {
        alert('Mismatched group ids in same context')
        return null
    } else {
        group_id = $(first).attr('group')
    }

    container = get_container(first)
    group_id = container.attr('id')
    group_id_cache = String(group_id)

    $.post("/cmds/combine/", data, function (data) {

        if (data.error) {
            error(data.error)
            return
        }

        nsym = first.after(data.new_html).next();

        //Render the TeX
        refresh_jsmath(container);

        //Find the root node and associate it with the
        //new container, the root node should be the only
        //one which the server didn't automatically
        //assign a new id to.
        container.find('[group=None]').attr('group', group_id_cache)

        first.remove();
        second.remove();

        var first_node = NODES[first.id()];
        var second_node = NODES[second.id()];

        //Make appropriate changes to the tree
        if (!data.new_json[0]) {
            first_node.delNode();
        } else {
            merge_json_to_tree(first_node, data.new_json[0]);
        }

        if (!data.new_json[1]) {
            second_node.delNode();
        } else {
            merge_json_to_tree(second_node, data.new_json[1]);
        }

        update(container);

        traverse_lines();
        cleanup_ajax_scripts();

        NAMESPACE_INDEX = data.namespace_index;
    }, "json");
}

function new_line(type) {
    data = {}
    data.namespace_index = NAMESPACE_INDEX;
    data.cell_index = CELL_INDEX;
    data.type = type

    $.post("/cmds/new_line/", data, function (data) {
        if (data.error) {
            error(data.error)
        }

        if (data.new_html) {
            //TOOD Simplify this mess
            new_cell_html = $(data.new_html);
            $("#workspace").append(new_cell_html);
            $('.lines').show();
            refresh_jsmath(new_cell_html);
            traverse_lines();

            var new_cell = new Cell();
            new_cell.dom = new_cell_html;
            var eq = build_tree_from_json(data.new_json);
            new_cell.equations.push(eq);

            CELLS.push(new_cell);
            CELL_INDEX = data.cell_index;

        }

        NAMESPACE_INDEX = data.namespace_index;
        $('.equation button','#workspace').parent().buttonset();
    }, 'json')
    cleanup_ajax_scripts();
}

function save_workspace() {
    data = {}
    i = 0

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
            error(data.error)
        }
        if (data.success) {
            error('Save succesfull.')
        }
    }, 'json')
}

function parse_pure() {
    var data = {}
    data.code = $('#pure_input').val()
    data.namespace_index = NAMESPACE_INDEX;
    data.cell_index = CELL_INDEX;

    $.post("/cmds/pure_parse/", data, function (data) {
        if (data.error) {
            error(data.error)
        }

        if (data.new_html) {
            //TOOD Simplify this mess
            new_cell_html = $(data.new_html);
            $("#workspace").append(new_cell_html);
            $('.lines').show();
            refresh_jsmath(new_cell_html);
            traverse_lines();

            var new_cell = new Cell();
            new_cell.dom = new_cell_html;
            var eq = build_tree_from_json(data.new_json);
            new_cell.equations.push(eq);

            CELLS.push(new_cell);
            CELL_INDEX = data.cell_index;

        }

        NAMESPACE_INDEX = data.namespace_index;
    }, 'json')
    cleanup_ajax_scripts();
}

function sage_inline(text) {
    var data = {}
    //    data.sage = $('#sage_text').val()
    data.sage = text

    $.post("sage_inline/", data, function (data) {
        if (data.error) {
            error(data.error)
            $("#sage_cmd").focus()
            return
        }

        obj = selection.nth(0);

        group_id = obj.attr('group');
        group_id_cache = String(group_id)

        nsym = obj.replace(data);
        nsym.attr('group', group_id_cache);
        refresh_jsmath($(nsym))

        $('body').focus()
        $('#cmd_input').hide();
        clear_selection();
    }, 'json')
}

///////////////////////////////////////////////////////////
// Tree Traversal
///////////////////////////////////////////////////////////

function get_common_parent(first, second) {
/*
       This traverses the tree upwards until it finds the branch that each element having in common

                         A
                       /   \
                      B     C
                     / \   / \
                    D   E F   G

     get_common_parent(D,E) = B
     get_common_parent(F,E) = A

     */

    //** Check to see if our elements are in disjoint branches **//
    //Yah, apparently the .find command can't strip the selector off a jquery() argument passed to it, lame
    if ($(first).find(second.selector).exists()) {
        return first
    }

    if ($(second).find(first.selector).exists()) {
        return second
    }

    //** Our elements are disjoint so ascend upwards recursively until we find the common parent**//
    first_container = get_container(first);
    return get_common_parent(first_container, second)

}

function get_common_context(first, second) {
/*
       This traverses the tree upwards a maximum one one level to see if two nodes share the same parent
       aka they are siblings

                         A
                       /   \
                      B     C
                     / \   / \
                    D   E F   G

     get_common_context(D,E) = B
     get_common_context(F,E) = null

     */
    first_container = get_container(first)

    if (!first_container) {
        return null
    }

    if (first_container.attr('id') == get_container(second).attr('id')) {
        return first_container
    } else {
        return null
    }
}

function get_nested(first, second) {

/*
       This traverses the tree upwards to see if two elements are nested

                         A
                       /   \
                      B     C
                     / \   / \
                    D   E F   G

     get_nested(D,B) = B
     get_nested(D,A) = A
     get_nested(D,E) = null

     */
    if ($(first).find(second.selector).exists()) {
        return first
    }

    if ($(second).find(first.selector).exists()) {
        return second
    }

    return null
}

function are_siblings(first, second) {
    //Convenience wrapper for checking if two elements are siblings
    return (get_common_context(first, second) != null)
}

function traverse_lines() {
    // jQuery tooltip croaks if we apply $.tooltip multiple times
    // so we just ignore elements that we've already initiated
    untooltiped = _.reject($('[math-type]','#workspace'), function(obj){ return obj.tooltipText });

    function make_tooltip(obj) {
        $(obj).tooltip({
            track:true,
            bodyHandler: $(this).attr('math-type'),
            fade: 250,
            delay: 1000,
        });
    }

    _.each(untooltiped, make_tooltip);

    unselectable = _.reject($('[math-meta-class=term]','#workspace'), function(obj){ return obj.selectable });
    
    function make_selectable(obj) {
        $(obj).click(function(event) {
            select_term(this);
            event.stopPropagation();
        });
        // Pass this object in subsequent interations
        obj.selectable = true;
    };

    _.each(unselectable, make_selectable);

    unselectable = _.reject($('[math-meta-class=term]:not(.placeholder)','#math_palette'), function(obj){ return obj.selectable });
    _.each(unselectable, make_selectable);

    resize_parentheses()
}

///////////////////////////////////////////////////////////
// Drag & Drop
///////////////////////////////////////////////////////////

//This is the functin django calls to init the sortable state of
//new objects
function make_sortable(object, connector, options) {
    //TODO: Add an option to disable all dragging and hover
    //states in the worksheet
    
    group_id = $(object).attr('id');
    $(object).sortable(options)
}

///////////////////////////////////////////////////////////
// Math Parsing & Generating
///////////////////////////////////////////////////////////

function check_container(object) {
    //This handles stupid expression checking that is too expensive to do via Ajax, ie removing infix sugar 
    _.each(object.children(), function () {
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

function get_container(object) {
    if (object.attr('group') == object.attr('id')) {
        //console.log('Object: '+$(object).attr('math')+' is own parent.');
    }
    if (object.attr('group') != undefined && object.attr('toplevel') != 'true') {
        return $('#' + object.attr('group'))
    }
    else {
        //console.log('Object: '+$(object).attr('math')+' is orphaned.');
    }
}

function is_toplevel(object) {
    //If container is RHS or LHS we consider it toplevel
    context = get_container($(object)).attr('math-type');
    if (context == 'LHS' || context == 'RHS') {
        return true;
    }
    else {
        return false;
    }
}

//This should be called after each change to the workspace


function update(object) {
    if (object != undefined) {
        if (object.attr('locked') != 'true') {
            check_combinations(object);
            check_container(object);
            //check_combinations(object);
            update_math(object);
        }
    }
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

function refresh_jsmath(element) {
    //Refresh math for a specific element
    if (element) {
        //Toggling visiblity prevents the underlying TeX from
        //showing
        element.css('visibility', 'hidden')
        jsMath.ConvertTeX(element[0])
        jsMath.ProcessBeforeShowing(element[0])
        $(function () {
            element.css('visibility', 'visible')
        })
    }
    //Refresh math Globally, shouldn't be called too much because
    //it bogs down the browser
    else {
        jsMath.ConvertTeX()
        jsMath.ProcessBeforeShowing()
    }
}

function update_math(object, stack_depth) {
/*Take a CONTAINER object iterate over all elements 
      that point to it and then incorporate their math
      strings into ours, then ascend upwards doing the same*/

    if (!stack_depth) {
        stack_depth = 1
    } else {
        stack_depth += 1
    }

    if (stack_depth > 25) {
        alert('fuck, maximum recursion depth reached' + $(object).attr('id') + ',group:' + $(object).attr('group'))
        return null
    }

    var mst = new String;

    self_id = object.attr('id');

    members = $('#' + self_id + ' *[group=' + object.attr('id') + ']');

    //If we have an empty container
    if (members.length == 0) {
        mst = 'None';
    }

    //TODO: Remove $.each
    $.each(members, function () {
        if ($(this).attr("math") != undefined) {
            mst += $(this).attr("math") + ' ';
        }
    });

    mst = '(' + object.mathtype() + ' ' + mst + ')';

    object.attr('math', mst);
    object.attr('num_children', members.length)

    if (object.attr('group') != undefined) {
        group = $('#' + object.attr('group'));
        update_math(group, stack_depth)
    }
}

function visualize_tree(tree) {

    if (!tree) {
        if (NODES[selection.nth(0).id()]) {
            tree = NODES[selection.nth(0).id()].tree;
        }
        else {
            error('Could not create tree from selection');
            return;
        }
    }

    var json = nested_json(tree);

    if (!json) {
        error('Could not generate JSON from object');
        return;
    }

    if (active_graph) {
        st = active_graph;
        st.canvas.clear();

        var lbs = st.fx.labels;
        for (var label in lbs) {
            if (lbs[label]) {
                lbs[label].parentNode.removeChild(lbs[label]);
            }
        }

        st.fx.labels = {};

        st.loadJSON(json);
        st.compute();
        st.onClick(st.root);
        active_graph = st;

        //active_graph.op.morph(json, {  
        //      type: 'replot',  
        //      duration: 1500, 
        //      hideLabels: false
        //});   
        return;
    }

    var canvas = __CANVAS__;
    canvas.clear();

    var st = new ST(canvas, {
        duration: 100,
        transition: Trans.Quart.easeInOut,
        levelDistance: 50,
        orientation: 'top',
        clearCanvas: true,

        Node: {
            height: 20,
            width: 60,
            type: 'rectangle',
            color: '#F7FBFF',
            overridable: true,
        },

        Edge: {
            type: 'bezier',
            overridable: true,
            lineWidth: 2,
            color: '#ccc',
        },

        onCreateLabel: function (label, node) {
            label.id = node.id;
            label.innerHTML = node.name;

            label.onclick = function () {
                st.onClick(node.id);
            };

            $(label).bind('mouseover', function () {
                node.data.dom.addClass('ui-state-highlight');
            })
            $(label).bind('mouseout', function () {
                node.data.dom.removeClass('ui-state-highlight');
            })
            var style = label.style;
            style.width = 60 + 'px';
            style.height = 17 + 'px';
            style.cursor = 'pointer';
            style.color = '#333';
            style.fontSize = '0.8em';
            style.textAlign = 'center';
            style.paddingTop = '3px';
        },

        onBeforePlotNode: function (node) {
            if (node.selected) {
                node.data.$color = "#ff7";
            }
            else {
                delete node.data.$color;
                var GUtil = Graph.Util;
                if (!GUtil.anySubnode(node, "exist")) {
                    depth = node._depth
                    node.data.$color = ['#F7FBFF', '#DEEBF7', '#C6DBEF', '#9ECAE1', '#6BAED6', '#4292C6'][depth];
                }
            }
        },

        onBeforePlotLine: function (adj) {
            if (adj.nodeFrom.selected && adj.nodeTo.selected) {
                adj.data.$color = '#000';
                adj.data.$lineWidth = 3;
            }
            else {
                delete adj.data.$color;
                delete adj.data.$lineWidth;
            }
        }
    });
    st.loadJSON(json);
    st.compute();
    st.onClick(st.root);

    active_graph = st;
}

function dropin(old, nwr) {
    //Drop an element in place of another, preserving group linkings
    group_id = old.attr('group');
    nwr.attr('group', group_id);
    nwr.hide();
    old.fadeOut(function () {
        nsym = old.after(nwr);
    });
}

function get_equation(object) {
    eq = $(object).parents("tr");
    return (eq)
}

function get_lhs(object) {
    return $(get_equation(object).find('[math-type=LHS]'));
}

function get_rhs(object) {
    return $(get_equation(object).find('[math-type=RHS]'));
}


function duplicate_placeholder(placeholder) {
    //This is used for duplicating placeholders in container type
    //objects i.e. (Addition, Multiplication)
    //placeholder = get_selection(0)
    if (placeholder.attr('math-type') == 'Placeholder') {
        nsym = placeholder.clone()
        nsym.unbind()
        nsym.attr('id', 'destroyme')
        placeholder.after(nsym)
        check_combinations(get_container(placeholder))
    }
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
        clear_selection()
        select_term(first)
        return
    }

    placeholders = $('.lines .placeholder')

    var i = 0;
    for (i = 0; i <= placeholders.length; i++) {
        if ($(placeholders[i]).attr('id') == $(start).attr('id')) {
            if (i === placeholders.length) {
                clear_selection()
                select_term($(placeholders[1]))
            }
            else {
                clear_selection()
                select_term($(placeholders[i + 1]))
            }
        }
    }

/*
    if(get_container(start) != undefined)
    {
        console.log('Jumping up')
        next_placeholder(get_container(start))
    }
    */
}


//function substite_addition() {
//    placeholder = get_selection(0)
//    if (placeholder.attr('math-type') == 'Placeholder') {
//        if (get_container(placeholder).attr('math-type') == 'Addition') {
//            add_after(placeholder, '(Placeholder )')
//        }
//        else {
//            replace_manually(placeholder, '(Addition (Placeholder ) (Placeholder ))')
//        }
//    }
//    else {
//        if (get_container(placeholder).attr('math-type') == 'Addition') {
//            add_after(placeholder, '(Placeholder )')
//        }
//    }
//
//}
//
//function substite_multiplication() {
//    placeholder = get_selection(0)
//    if (placeholder.attr('math-type') == 'Placeholder') {
//        if (get_container(placeholder).attr('math-type') == 'Product') {
//            add_after(placeholder, '(Placeholder )')
//        }
//        else {
//            replace_manually(placeholder, '(Product (Placeholder ) (Placeholder ))')
//        }
//    }
//    else {
//        if (get_container(placeholder).attr('math-type') == 'Product') {
//            add_after(placeholder, '(Placeholder )')
//        }
//    }
//}

function remove_element() {
    var placeholder = selection.nth(0)
    var container = get_container(placeholder)

    if (placeholder.node().depth == 1 && selection.__lst.length == 1) {
        NODES[placeholder.id()].delNode();
        placeholder.remove()
        clear_selection()
        return;
    }

    if (placeholder.attr('math-type') == 'RHS' || placeholder.attr('math-type') == 'LHS') {
        return;
    }

    if (container) {
        if (container.attr('math-type') == 'RHS' || container.attr('math-type') == 'LHS') {
            return;
        }

        if (container.attr('math-type') == 'Addition' || container.attr('math-type') == 'Product') {
            if (parseInt(container.attr('num_children')) > 1) {
                container = get_container(placeholder)
                container_cache = String(container.selector)
                placeholder.remove()
                clear_selection()
                update($(container_cache))
            }
            else {
                apply_transform('Replace', [placeholder.math(), '(Placeholder )'])
                //replace_manually(placeholder, '(Placeholder )')
            }
        }
        else {
            apply_transform('Replace', [placeholder.math(), '(Placeholder )'])
            //replace_manually(placeholder, '(Placeholder )')
        }
    }
}

//function substite_subtraction() {
//    placeholder = get_selection(0)
//    if (get_container(placeholder).attr('math-type') == 'Addition') {
//        add_after(placeholder, '(Negate (Placeholder ))')
//    }
//    else {
//        replace_manually(placeholder, '(Addition (Negate (Placeholder )))')
//    }
//}
//
//function substite_division() {
//    placeholder = get_selection(0)
//    replace_manually(placeholder, '(Fraction (Placeholder ) (Placeholder ) )')
//}

function replace_manually(obj, code) {
    data = {}
    data.first = selection.nth(0).attr('math')
    data.second = code
    data.transform = 'Replace'

    $.post("/cmds/apply_transform/", data, function (data) {

        if (data.error) {
            error(data.error)
            clear_selection()
            return
        }

        //Remove terms (if needed)
        if (data.remove == 'first') {
            obj.remove();
        }

        //Swap the first term
        if (data.first) {
            group_id = obj.attr('group');
            group_id_cache = String(group_id)


            nsym = obj.replace(data.first);
            nsym.attr('group', group_id_cache);

            refresh_jsmath($(nsym))

        }

        clear_selection()
        traverse_lines();
        update(get_container(obj))
    }, "json");
    cleanup_ajax_scripts()
    clear_lookups()
}

function add_after(obj, code) {
    // Apply PlaceholderSubstitute with the given code argument
    data = {}
    data.first = '(Placeholder )'
    data.second = code
    data.transform = 'Replace'

    $.post("/cmds/apply_transform/", data, function (data) {

        if (data.error) {
            error(data.error)
            clear_selection()
            return
        }

        if (data.first) {
            group_id = obj.attr('group');
            group_id_cache = String(group_id)

            nsym = obj.after(data.first).next();
            nsym.attr('group', group_id_cache);

            refresh_jsmath($(nsym))
        }

        traverse_lines();
        update(get_container(obj))
    }, "json");
    cleanup_ajax_scripts()
    clear_lookups()
}

function preview() {
    var tex = $('#texinput').val();
    $('#preview').html('$$' + tex + '$$');
    refresh_jsmath();
}

function new_symbol() {
    $.post('/sym/0/?new=true', function (response) {
        $('#new_symbol').html(response);
        $("#new_symbol").dialog({
            modal: true,
            resizable: false,
            position: 'center'
        });
        refresh_jsmath();
        $('#form_new_symbol').submit(function () {
            shareData = $(this).serialize();
            $.post('/sym/new/', shareData);
            return false;
        });
        $("#new_symbol").dialog("option", "width", 520);
    });
}
