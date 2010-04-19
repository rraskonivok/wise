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

$.fn.exists = function(){return jQuery(this).length>0;}

$.fn.replace = function(htmls){
      var replacer = $(htmls);
        $(this).replaceWith(replacer);
          return replacer;
};

$.fn.swap = function(b) {
    b = jQuery(b)[0];
    var a = this[0];

    var t = a.parentNode.insertBefore(document.createTextNode(''), a);
    b.parentNode.insertBefore(a, b);
    t.parentNode.insertBefore(b, t);
    t.parentNode.removeChild(t);

    return this;
};

$.extend($.fn.disableTextSelect = function() {
        return this.each(function(){
                if($.browser.mozilla){//Firefox
                        $(this).css('MozUserSelect','none');
                }else if($.browser.msie){//IE
                        $(this).bind('selectstart',function(){return false;});
                }else{//Opera, etc.
                        (this).mousedown(function(){return false;});
                }
        });
});

function error(text)
{
   $('#error_dialog').text(text);
   $('#error_dialog').dialog({modal:true,dialogClass:'alert'});
}

function dialog(text)
{
   $('#error_dialog').text(text);
   $('#error_dialog').dialog({modal:true,dialogClass:'alert'});
}

function handle_equation(object)
{
    lhs = $(object.find('.lhs'));
    rhs = $(object.find('.rhs'));
}

function cleanup_ajax_scripts()
{
    //The ensures that any <script> tags inserted via ajax don't get executed more than once
    $("script[data-type=ajax]").remove()
}

$(document).ajaxStart(function(){$('#ajax_loading').show()})
$(document).ajaxStop(function(){$('#ajax_loading').hide()})

function connect_to_every_sortable(object)
{
    $(object).children().draggable({
        connectToSortable: $('.ui-sortable'),
        helper: 'clone',
        appendTo: 'body',
    });
}

function reset_selections()
{
    $().live('li[math-meta-class=term]',function(object){select_term(this)});
}

function fade_and_destroy(object)
{
    $(object).fadeOut('fast',function(){
        $(object).remove();
    });
}

function fade_old_new(old,news)
{
    $(old).hide('slow',function() {
        $(news).show(function() {
            $(old).remove();
        });
    });
}

function debug_math()
{
    $.each($('[math]'),function() {
        $(this).attr('title',$(this).attr('math'));
    });
}

function toggle_spacing()
{
    $('.container').css('vertical-align','baseline')
}

function toggle_units()
{
    $("body .unit").fadeOut();    
}

function select_term(object)
{
    //Since the selections have changed clear any looked-up (is that even a word?) actions
    clear_lookups()
    $("#selectionlist").fadeIn()


    clickedon = $(object)
    if(clickedon.hasClass('selected'))
    {
        clickedon.removeClass('selected');
        id = clickedon.attr("id");
        $.each($("#selectionlist button"),function()
        {
            if($(this).attr('pointer') === id)
            {
                $(this).remove(); 
            }
        });
    }
    else
    {
        clickedon.addClass('selected');
        typ = clickedon.attr('math-type');
        li = $(document.createElement('button')).html(typ)
        li.button()
        cancel = $(document.createElement('div'))
        cancel.addClass('ui-icon')
        cancel.addClass('ui-icon-close')
        cancel.css('float','left')
        cancel.css('cursor','pointer')
        li.prepend(cancel)
        li.attr('pointer',clickedon.attr('id'))
        li.attr('math-type',clickedon.attr('math-type'))
        cancel.attr('pointer',clickedon.attr('id'))

        li.bind('mouseover',function()
            {
                id = $(this).attr('pointer') 
                $('#'+id).css('background','#DD9090'); 
            });
        li.bind('mouseout',function()
            {
                id = $(this).attr('pointer') 
                $('#'+id).css('background','inherit'); 
            });
        cancel.bind('click',function()
            {
                ($(this).parent().remove())
                id = $(this).attr('pointer') 
                $('#'+id).removeClass('selected');
                $('#'+id).css('background','inherit'); 
                format_selection()
            });

        placed = $("#selectionlist").append(li);
        clickedon.effect('transfer',{ to: li, className: 'ui-effects-transfer' },400)
        format_selection();
    //Bind to select object command
    }
    
    if(num_selected() > 1 && get_selection(0).attr('math-type') == 'Placeholder')
    {
        apply_transform('PlaceholderSubstitute')
    }
}

function format_selection()
{
    $($("#selectionlist").children()).css('background-color','#9CBD86');
    $($("#selectionlist").children()[0]).css('border','2px solid #DD9090');
    $($("#selectionlist").children()[1]).css('border','2px solid #989cd7');
}

function num_selected()
{
    //The number of elements in the selection queue:
    return $("#selectionlist").children().length
}

function get_selection(n)
{
    //Return the nth selected item
    return $('#'+$($("#selectionlist").children()[n]).attr('pointer'));
}

 // ---------------------------------------------
 //  Lookups
 // -------------------------------------------

function lookup_transform()
{
    first = get_selection(0);
    second = get_selection(1);
    first_type = first.attr('math-type');
    second_type = second.attr('math-type');

    data = {}
    data.first = first_type
    data.second = second_type

    if(get_nested(first,second) != null)
    {
        data.nested = true
    }
    else
    {
        data.nested = false
    }

    context = get_common_context(first,second)

    if(context != null)
    {
        context = context.attr('math-type') 
    }

    data.context = context

    $.post("lookup_transform/",data, function(data)
        {
            $('#selectionlist').hide()
            $('#options').html(data);
            $('#options').fadeIn();
            $('#options button').button()
            refresh_jsmath()
        }
    ,'html')
}

function lookup_identity()
{
    first = get_selection(0);
    first_type = first.attr('math-type');

    data = {}
    data.first = first_type

    $.post("lookup_identity/",data, function(data) 
        {
            $('#options').html(data);
            $('#options').fadeIn();
        }
    ,'html')
}

function clear_lookups()
{
    $('#options').fadeOut()
}

function get_common_parent(first,second)
{
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
    if($(first).find(second.selector).exists()) {
        return first 
    }

    if($(second).find(first.selector).exists()) {
        return second  
    }

    //** Our elements are disjoint so ascend upwards recursively until we find the common parent**//
    first_container = get_container(first);
    return get_common_parent(first_container,second) 

}

function get_common_context(first,second)
{
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

    if(!first_container)
    {
        return null
    }

    if(first_container.attr('id') == get_container(second).attr('id')) {
       return first_container 
    } else {
       return null 
    }
}

function get_nested(first,second)
{

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
    if($(first).find(second.selector).exists()) {
        return first 
    }

    if($(second).find(first.selector).exists()) {
        return second  
    }

    return null
}

function are_siblings(first,second)
{
    //Convenience wrapper for checking if two elements are siblings
    return (get_common_context(first,second) != null)
}


function construct_numeric(num)
{
    term = $(document.createElement('span')).html('$$'+num+'$$')
    term.attr('math','(Numeric ' + num + +')')
    term.attr('math-meta-type','term')
    term.attr('math-type','Numeric')
    return(term)
}

function clear_selection()
{
    $.each($("#selectionlist button"),function() {
                $(this).remove(); 
        });
    $('.selected').removeClass('selected');
    $('#options').hide();
    $('#selectionlist').fadeIn();
}

function traverse_lines()
{
    //Traverse the lines of the workspace and make them sortable equations
    $.each($('#lines').find('tr'),function()
    {
        handle_equation($(this));
    });

    $('#workspace [title]').tooltip({track:true});

    $('[math-meta-class=term]').unbind('click');
    $('[math-meta-class=term]').unbind('click');

    $('*[math-meta-class=term]').click(
            function(event) {
                select_term(this); event.stopPropagation() 
            });
    //$('.pnths').css('height',function(){return $(this).parent().height()+20})
    
    //Let's try something else because jQuery is being funky with nested sortables 
    //connect_to_every_sortable(".palette");

    resize_parentheses()
    //Webkit requires that we run this twice
    resize_parentheses()

    $('.equation button').parent().buttonset();
}

function resize_parentheses()
{
    //Scale parentheses
    $.each($('.pnths'), function(obj)
        {
            parent_height = $(this).parent().height();
            $(this).height(parent_height)
            $(this).css('top',-parent_height/2)
        });
}

function term_spacing(x,y)
{
    if(x)
    {
        $('.term').css('padding-right',x)
        $('.term').css('padding-left',x)
    }

    if(y)
    {
        $('.term').css('padding-top',y)
        $('.term').css('padding-bottom',y)
    }
}

function make_sortable(object,connector,options)
{
    //TODO: Add an option to disable all dragging and hover
    //states in the worksheet

    //console.log([$(object),$(connector)]);
    group_id = $(object).attr('id');
    $(object).sortable(options)
    console.log(object,options)
}

function dragging(sort_object,ui)
{
    drag_x = ui.offset.left
    drag_y = ui.offset.top
    container = get_container(ui.item);
    if(container == null)
    {
        return false;
    }
    container_x = container.offset().left
    container_y = container.offset().top
    difference_y = Math.abs(container_y - drag_y)
    if(difference_y > 120)
    {
        $(sort_object).sortable('disable');
        $(sort_object).sortable('destroy');
        down(container,ui.item);
    }
}

/*
function down(container,dragged)
{
    if(is_toplevel(container))
    {
        equation = get_equation(dragged)
        var data = {}
        data.dragged = $(dragged).attr('math') 
        data.equation = equation.attr('math')
        $.post("topdown/", data,
           function(data) {
                equation.after(data);
                equation.remove()
                jsMath.ConvertTeX(); jsMath.Process();
                dragged.remove();
                traverse_lines();
           }, "html");
    }
    else
    {
        var data = {}
        data.container = $(container).attr('math') 
        data.dragged = $(dragged).attr('math') 
        data.context = get_container(container).attr('math-type'); 
        $.post("down/", data,
           function(data) {
                group_id = container.attr('group')
                nsym = container.after(data);
                container.siblings().attr('group',group_id);
                jsMath.ConvertTeX(); jsMath.Process();
                container.remove();
                dragged.remove();
                traverse_lines();
           }, "html");
    }
    cleanup_ajax_scripts()
}
*/

function get_equation(object)
{
    eq = $(object).parents("tr");
    return(eq)
}

function get_lhs(object)
{
    return $(get_equation(object).find('[math-type=LHS]'));
}

function get_rhs(object)
{
    return $(get_equation(object).find('[math-type=RHS]'));
}

function receive(ui,receiver,group_id)
{
    group_id = receiver.attr('id')

    obj = ui.item
    //If we drop an element in make sure we associate it with the group immediately
    obj.attr('group',group_id);

    //If we drag from a jquery draggable then the ui.item doesn't exist here yet
    //so just remap all the children with the group... this should be safe (right?)
    receiver.children('[math]').attr('group',group_id)

    //TODO do we need this?
    //update_math(ui.sender);

    //Make sure nothing is changed while we process the request
    receiver.attr('locked','true')

    data = {
        //The math of the dragged object 
        obj: ui.item.attr('math'),
        obj_type: ui.item.attr('math-type'),

        //The math of the receiving object
        receiver: receiver.attr('math'),
        receiver_type: receiver.attr('math-type'),
        receiver_context: get_container(receiver).attr('math-type'),

        //The math of the sender object
        sender: ui.sender.attr('math'),
        sender_type: ui.sender.attr('math-type'),
        sender_context: get_container(ui.sender).attr('math-type'),
        
        //The new position of the dragged obect inside receiver
        new_position: ui.item.parent().children("[math]").index(ui.item),
    }
    $.post("receive/", data,
           function(data){
            nsym = obj.replace(data);
            nsym.attr('group',group_id);
            refresh_jsmath($(nsym))
            receiver.attr('locked','false');
            update(get_container(nsym))
          },
        "html");
    cleanup_ajax_scripts()

}

function remove(ui,removed)
{
    //TODO: Do we need to call this?

    group_id = removed.attr('id')
    obj = ui.item
    removed.attr('locked','true')

    data = {
        //The math of the dragged object 
        obj: ui.item.attr('math'),
        obj_type: ui.item.attr('math-type'),

        //The math of the sender object
        sender: removed.attr('math'),
        sender_type: removed.attr('math-type'),
        sender_context: get_container(removed).attr('math-type'),
    }
    $.post("remove/", data,
           function(data){
                if(data)
                {
                    nsym = $(data).appendTo(removed);
                    nsym.attr('group',group_id);
                    refresh_jsmath($(nsym))
                    removed.attr('locked','false')
                    update_math(removed);
                }
          },
        "html");
    cleanup_ajax_scripts()
}

function whatisit(object)
{
    return $(object).attr('id')+', '+$(object).attr('math-type')+', '+$(object).attr('math')
}

function check_container(object)
{
    //This handles stupid checks that are too expensive to do via Ajax, ie removing infix sugar and whatnot
    $.each(object.children(), function()
        {
           prev = $(this).prev();
           cur = $(this);
           next = $(this).next();
           last = $(object).children(':last-child');
           first = $(object).children(':first-child');
           group = $(this).attr('group');
           if(group != "")
           {
               
               //Rules for handling parenthesis

               //This forces left parenthesis over to the left
               if(cur.hasClass('term') && next.hasClass('pnths') && next.hasClass('left'))
               {
                   cur.swap(next)
               }

               //This forces left parenthesis over to the left
               if(cur.hasClass('pnths') && next.hasClass('term') && cur.hasClass('right'))
               {
                   cur.swap(next)
               }

               //Rules for cleaning up infix sugar

               group_type = $('#'+group).attr('math-type');

               //  A + + B  --> A  + B
               if(cur.hasClass('infix') && next.hasClass('infix'))
               {
                    cur.remove();
               }

               // A + - B  --> A - B
               if(cur.hasClass('infix') && next.attr('math-type') == 'Negate')
               {
                    cur.remove();
               }
               
               //  ( + A  --> ( A
               if(cur.hasClass('pnths') && next.hasClass('infix'))
               {
                    next.remove() 
               }

               //  + ) --> )
               if(cur.hasClass('infix') && next.hasClass('pnths'))
               {
                    cur.remove() 
               }
                
               // + A + B --> A + B
               if(first.hasClass('infix'))
               {
                   first.remove();
               }

               // A + B + --> A + B
               if(last.hasClass('infix'))
               {
                   last.remove();
               }

           }
        });
}

function check_combinations(object){
    //Check to see if two terms are explicitly dragged next to each other and 
    //query the server to see if we can combine them into something

    if($(object).attr('locked') == 'true')
    {
       return 
    }
    $.each(object.children(), function()
        {
           prev = $(this).prev();
           cur = $(this);
           next = $(this).next();
           group = $(this).attr('group');
           if(group != "")
           {
               group_type = $('#'+group).attr('math-type');

               // A + B C + D -> A + combine(B,C) + D
               if(cur.attr('math-meta-class')=='term' && next.attr('math-meta-class')=='term')
               {
                   //The one exception (i.e. filthy hack) is that
                   //dragging a negated term next to any other
                   //doesn't induce the combine command since the
                   //negation sign on the negated term pretends
                   //it is sugar, long story short it looks
                   //prettier
                   
                   if(next.attr('math-type') != 'Negate')
                   {
                       combine(cur,next,group_type);
                       check_container(object)
                   }
               }
           }
        });
}

function combine(first,second,context)
{
    data = {};
    data.context = context
    data.first = $(first).attr('math');
    data.second = $(second).attr('math');

    if($(first).attr('group') != $(second).attr('group'))
    {
        alert('Mismatched group ids in same context')
        return null
    } else { 
        group_id = $(first).attr('group')
    }

    container = get_container(first)
    group_id = container.attr('id')
    group_id_cache = String(group_id)

    $.post("combine/", data,
           function(data){
                nsym = first.after(data).next();
                container.find('[group=None]').attr('group',group_id_cache)
                first.remove();
                second.remove();
                update(container);
                refresh_jsmath($(container))
                traverse_lines();
                cleanup_ajax_scripts();
          },
        "html");
}

function get_container(object)
{
    if(object.attr('group') == object.attr('id'))
    {
        //console.log('Object: '+$(object).attr('math')+' is own parent.');
    }
    if(object.attr('group') != undefined && object.attr('math-type') != 'Equation')
    {
        return $('#'+object.attr('group'))
    }
    else
    {
        //console.log('Object: '+$(object).attr('math')+' is orphaned.');
    }
}

function is_toplevel(object)
{
    //If container is RHS or LHS tag this is toplevel and perform division on entire equation instead of factoring out a term
    context = get_container($(object)).attr('math-type');
    if(context == 'LHS' || context == 'RHS') 
    {
        return true;
    }
    else {
        return false;
    }
}

function debug_colors(object)
{
    $('li[math-meta-class=term]').css('border-bottom','5px solid red');
    $('ul[math-type]').css('border-bottom','5px solid blue');
    $('.rhs').css('border-bottom','none');
    $('.lhs').css('border-bottom','none');
    $('.equation').css('background-color','#CCCCCC');
    $('.rhs').css('background-color','#FFCCCC');
    $('.lhs').css('background-color','#CCFF00');
}

function serialize_object(saveData)
{
    var a = [];
    for (key in saveData) {
            a.push(key+"="+saveData[key]);
    }
    var serialized = a.join("&")
    return serialized;
}

//This should be called after each change to the workspace
function update(object)
{
    if(object != undefined)
    {
        if(object.attr('locked') != 'true')
        {
            check_combinations(object);
            check_container(object);
            check_combinations(object);
            clear_selection();
            reset_selections();
            update_math(object);
        }
    }
}

function refresh_jsmath(element)
{
    //Refresh math for a specific element
    if(element)
    {
        //Toggling visiblity prevents the underlying TeX from
        //showing
        element.css('visibility','hidden')
        jsMath.ConvertTeX(element[0])
        jsMath.ProcessBeforeShowing(element[0])
        $(function() { element.css('visibility','visible') })
    }
    //Refresh math Globally
    else
    {
        jsMath.ConvertTeX()
        jsMath.ProcessBeforeShowing()
    }
}

function update_math(object,stack_depth)
{
    /*Take a CONTAINER object iterate over all elements 
      that point to it and then incorporate their math
      strings into ours, then ascend upwards doing the same*/

    if(!stack_depth)
    {
        stack_depth = 1
    } else {
        stack_depth += 1
    }

    if(stack_depth > 25)
    {
        alert('fuck, maximum recursion depth reached' + $(object).attr('id') + ',group:' + $(object).attr('group')  )
        return null
    }

    mst = new String;

    self_id = object.attr('id')

    members = $('#' + self_id + ' *[group='+object.attr('id')+']');

    //If we have an empty container
    if(members.length == 0)
    {
        mst = 'None'
    }

    $.each(members,function()
    {
        if($(this).attr("math") != undefined)
        {
            mst += $(this).attr("math") + ' ';
        }
    });

    mst = '(' + object.attr('math-type') + ' ' +  mst + ')';

    object.attr('math',mst); 

    if(object.attr('group') != undefined)
    {
        group = $('#'+object.attr('group'));
        update_math(group,stack_depth);
    }
}

function pass_array(object)
{
    /* A little bit of recursive magic */
    //a = object.sortable('serialize',{attribute: 'math'});
    //b = object.sortable('toArray');
    /* We can only do one task at a time otherwise indeces get screwed up*/
    a = $.map(object.children(),function(i)
    {
        return $(i).attr("math");
    });
    b = $.map(object.children(),function(i)
    {
        return $(i).attr("math-type");
    });
    c = $.map(object.children(),function(i)
    {
        if($(i).attr('math')!=undefined)
        {
            return $(i).attr("id");
        }
    });
}

function get_info(object)
{
    a = $(object).attr("math");
    b = $(object).attr("math-type");
    c = $(object).attr("id");
    return { math: a, type: b, id: c }
}

function dropin(old,nwr)
{
    //Drop an element in place of another, preserving group linkings
    group_id = old.attr('group');
    nwr.attr('group',group_id);
    nwr.hide();
    old.fadeOut(function() {
        nsym = old.after(nwr);
    });
}

function apply_transform(transform)
{
    data = {}
    data.first = get_selection(0).attr('math')
    data.second = get_selection(1).attr('math')
    data.transform = transform

    $.post("apply_transform/", data,
        function(data){
            //TODO this really needs to be cleaned up 

            if(data.error)
            {
                error(data.error)
                clear_selection()
                return
            }
            
            //Remove terms (if needed)
            if(data.remove == 'first')
            {
                get_selection(0).remove();
            }

            if(data.remove == 'second')
            {
                get_selection(1).remove();
            }

            //Swap the first term
            if(data.first)
            {
                obj = get_selection(0);
                group_id = obj.attr('group');
                group_id_cache = String(group_id)


                nsym = obj.replace(data.first);
                nsym.attr('group',group_id_cache);

                refresh_jsmath($(nsym))

                //refresh_jsmath()
            }
            //Swap the second term
            if(data.second)
            {
                obj = get_selection(1);
                group_id = obj.attr('group');
                group_id_cache = String(group_id)

                nsym = obj.replace(data.second);
                nsym.attr('group',group_id_cache);

                refresh_jsmath($(nsym))
                //refresh_jsmath()
            }

            clear_selection()
            traverse_lines();
            update(get_container(obj))
        },
        "json");
    cleanup_ajax_scripts()
    clear_lookups()
}

function apply_identity(identity)
{
    data = {}
    data.first = get_selection(0).attr('math')
    data.identity = identity

    $.post("apply_identity/", data,
        function(data){
            //TODO this really needs to be cleaned up 
            //Swap the first term
            obj = get_selection(0);
            group_id = $(obj).attr('group');
            //Yah, don't even try to understand why we need to cache this.... this is VERY odd
            group_id_cache = String(group_id)
            nsym = obj.replace(data.first);
            nsym.attr('group',group_id_cache);
            refresh_jsmath()
            clear_selection()
            traverse_lines();
            update(get_container(obj))
        },
        "json");
    cleanup_ajax_scripts()
    clear_lookups()
}

function show_debug_menu()
{
    $('#debug_menu').dialog();
    $('#horizslider').slider({
        slide:
        function(e,ui)
        {
            term_spacing(ui.value,null)
        }}
    );
    $('#vertslider').slider({
        slide:
        function(e,ui)
        {
            term_spacing(null,ui.value)
        }}
    );
}

function toggle_sageinput()
{
    $('#sage_input').dialog();
}

function parse_sage()
{
    var data = {}
    data.sage = $('#sage_text').val()
    $.post("sage_parse/", data ,
        function(data){
            if(data.error) {
                error(data.error)
            }
            if(data.newline) {
                $('#lines').append(data.newline)
                refresh_jsmath($(data.newline))
            }
            traverse_lines();
        }
        ,'json')
}

function bind_hover_toggle(){
    $('#hovertoggle').toggle(
        function()
        {
            $('#workspace .term[math]').hover(
                function()
                {
                    $(this).addClass('term_hover')
                }
                ,
                function()
                {
                    $(this).removeClass('term_hover')
                }
            )

            $('#workspace .container[math]').hover(
                function()
                {
                    $(this).addClass('container_hover')
                }
                ,
                function()
                {
                    $(this).removeClass('container_hover')
                }
            )
        }
        ,
        function()
        {
            $('#workspace .term[math]').hover(
                function()
                {
                    $(this).removeClass('term_hover')
                }
            )
            $('#workspace .container[math]').hover(
                function()
                {
                    $(this).removeClass('container_hover')
                }
            )
        })
}

function new_inline(){
    data = {}
    $.post("new_inline/", data ,
        function(data){
            if(data.error) {
                error(data.error)
            }
            if(data.newline) {
                $('#lines').append(data.newline)
            }
            traverse_lines();
            refresh_jsmath()
        }
    ,'json')
}

function cur_next(str)
{
    current = $('.selected');
    if(!current.exists())
    {
        next = $("#rhs");
    }
    if(current.children('ul li').exists())
    {
        next = current.children('ul li');
    }
    else
    {   
        next = current.next();
        if(!next.exists())
        {
            next = current.parent().next();
        }
    }
    next.addClass('selected');
    current.removeClass('selected');
}


function cur_prev(str)
{
    current = $('.selected');
    prev = current.prev();
    if(!prev.exists())
    {
        prev = current.parent().prev();
    }
    prev.addClass('selected');
    current.removeClass('selected');
}

function save_workspace()
{
    data = {}
    i = 0

    $.each($("tr.equation"),
        function(obj)
        { 
                data[i] = $(this).attr('math')
                i += 1
        })

    //Flash the border to indicate we've saved.
    $('#workspace').animate({ border: "5px solid red" }, 1000);
    $('#workspace').animate({ border: "0px solid black" }, 1000);

    $.post("save_workspace/", data ,
        function(data){
            if(data.error) {
                error(data.error)
            }
        }
        ,'json')
}

$(document).ready(function() {
    init();
}) 
