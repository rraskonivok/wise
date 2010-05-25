/*
 * jQuery Pines Notify (pnotify) Plugin 1.0.0 Beta 1
 *
 * Copyright (c) 2009 Hunter Perrin
 *
 * Licensed (along with all of Pines) under the GNU Affero GPL:
 *	  http://www.gnu.org/licenses/agpl.html
 */
(function(e){var q,m,k,n;e.extend({pnotify_remove_all:function(){var g=k.data("pnotify");g&&g.length&&e.each(g,function(){this.pnotify_remove&&this.pnotify_remove()})},pnotify_position_all:function(){m&&clearTimeout(m);m=null;var g=k.data("pnotify");if(g&&g.length){e.each(g,function(){var c=this.opts.pnotify_stack;if(c){if(!c.nextpos1)c.nextpos1=c.firstpos1;if(!c.nextpos2)c.nextpos2=c.firstpos2;if(!c.addpos2)c.addpos2=0;if(this.css("display")!="none"){var a,j,i={},b;switch(c.dir1){case "down":b="top";
break;case "up":b="bottom";break;case "left":b="right";break;case "right":b="left";break}a=parseInt(this.css(b));if(isNaN(a))a=0;if(typeof c.firstpos1=="undefined"){c.firstpos1=a;c.nextpos1=c.firstpos1}var h;switch(c.dir2){case "down":h="top";break;case "up":h="bottom";break;case "left":h="right";break;case "right":h="left";break}j=parseInt(this.css(h));if(isNaN(j))j=0;if(typeof c.firstpos2=="undefined"){c.firstpos2=j;c.nextpos2=c.firstpos2}if(c.dir1=="down"&&c.nextpos1+this.height()>n.height()||
c.dir1=="up"&&c.nextpos1+this.height()>n.height()||c.dir1=="left"&&c.nextpos1+this.width()>n.width()||c.dir1=="right"&&c.nextpos1+this.width()>n.width()){c.nextpos1=c.firstpos1;c.nextpos2+=c.addpos2+10;c.addpos2=0}if(c.animation&&c.nextpos2<j)switch(c.dir2){case "down":i.top=c.nextpos2+"px";break;case "up":i.bottom=c.nextpos2+"px";break;case "left":i.right=c.nextpos2+"px";break;case "right":i.left=c.nextpos2+"px";break}else this.css(h,c.nextpos2+"px");switch(c.dir2){case "down":case "up":if(this.outerHeight(true)>
c.addpos2)c.addpos2=this.height();break;case "left":case "right":if(this.outerWidth(true)>c.addpos2)c.addpos2=this.width();break}if(c.nextpos1)if(c.animation&&(a>c.nextpos1||i.top||i.bottom||i.right||i.left))switch(c.dir1){case "down":i.top=c.nextpos1+"px";break;case "up":i.bottom=c.nextpos1+"px";break;case "left":i.right=c.nextpos1+"px";break;case "right":i.left=c.nextpos1+"px";break}else this.css(b,c.nextpos1+"px");if(i.top||i.bottom||i.right||i.left)this.animate(i,{duration:500,queue:false});switch(c.dir1){case "down":case "up":c.nextpos1+=
this.height()+10;break;case "left":case "right":c.nextpos1+=this.width()+10;break}}}});e.each(g,function(){var c=this.opts.pnotify_stack;if(c){c.nextpos1=c.firstpos1;c.nextpos2=c.firstpos2;c.addpos2=0;c.animation=true}})}},pnotify:function(g){k||(k=e("body"));n||(n=e(window));var c,a;if(typeof g!="object"){a=e.extend({},e.pnotify.defaults);a.pnotify_text=g}else a=e.extend({},e.pnotify.defaults,g);if(a.pnotify_before_init)if(a.pnotify_before_init(a)===false)return null;var j,i=function(d,f){b.css("display",
"none");var o=document.elementFromPoint(d.clientX,d.clientY);b.css("display","block");var r=e(o),s=r.css("cursor");b.css("cursor",s!="auto"?s:"default");if(!j||j.get(0)!=o){if(j){p.call(j.get(0),"mouseleave",d.originalEvent);p.call(j.get(0),"mouseout",d.originalEvent)}p.call(o,"mouseenter",d.originalEvent);p.call(o,"mouseover",d.originalEvent)}p.call(o,f,d.originalEvent);j=r},b=e("<div />",{"class":"ui-pnotify "+a.pnotify_addclass,css:{display:"none"},mouseenter:function(d){a.pnotify_nonblock&&d.stopPropagation();
if(a.pnotify_mouse_reset&&c=="out"){b.stop(true);b.css("height","auto").animate({width:a.pnotify_width,opacity:a.pnotify_nonblock?a.pnotify_nonblock_opacity:a.pnotify_opacity},"fast")}else a.pnotify_nonblock&&c!="out"&&b.animate({opacity:a.pnotify_nonblock_opacity},"fast");a.pnotify_hide&&a.pnotify_mouse_reset&&b.pnotify_cancel_remove();a.pnotify_closer&&!a.pnotify_nonblock&&b.closer.show()},mouseleave:function(d){a.pnotify_nonblock&&d.stopPropagation();j=null;b.css("cursor","auto");a.pnotify_nonblock&&
c!="out"&&b.animate({opacity:a.pnotify_opacity},"fast");a.pnotify_hide&&a.pnotify_mouse_reset&&b.pnotify_queue_remove();b.closer.hide();e.pnotify_position_all()},mouseover:function(d){a.pnotify_nonblock&&d.stopPropagation()},mouseout:function(d){a.pnotify_nonblock&&d.stopPropagation()},mousemove:function(d){if(a.pnotify_nonblock){d.stopPropagation();i(d,"onmousemove")}},mousedown:function(d){if(a.pnotify_nonblock){d.stopPropagation();d.preventDefault();i(d,"onmousedown")}},mouseup:function(d){if(a.pnotify_nonblock){d.stopPropagation();
d.preventDefault();i(d,"onmouseup")}},click:function(d){if(a.pnotify_nonblock){d.stopPropagation();i(d,"onclick")}},dblclick:function(d){if(a.pnotify_nonblock){d.stopPropagation();i(d,"ondblclick")}}});b.opts=a;if(a.pnotify_shadow&&!e.browser.msie)b.shadow_container=e("<div />",{"class":"ui-widget-shadow ui-corner-all ui-pnotify-shadow"}).prependTo(b);b.container=e("<div />",{"class":"ui-widget ui-widget-content ui-corner-all ui-pnotify-container "+(a.pnotify_type=="error"?"ui-state-error":"ui-state-highlight")}).appendTo(b);
b.pnotify_version="1.0.0b1";b.pnotify=function(d){var f=a;if(typeof d=="string")a.pnotify_text=d;else a=e.extend({},a,d);b.opts=a;if(a.pnotify_shadow!=f.pnotify_shadow)if(a.pnotify_shadow&&!e.browser.msie)b.shadow_container=e("<div />",{"class":"ui-widget-shadow ui-pnotify-shadow"}).prependTo(b);else b.children(".ui-pnotify-shadow").remove();if(a.pnotify_addclass===false)b.removeClass(f.pnotify_addclass);else a.pnotify_addclass!==f.pnotify_addclass&&b.removeClass(f.pnotify_addclass).addClass(a.pnotify_addclass);
if(a.pnotify_title===false)b.title_container.hide("fast");else a.pnotify_title!==f.pnotify_title&&b.title_container.html(a.pnotify_title).show(200);if(a.pnotify_text===false)b.text_container.hide("fast");else if(a.pnotify_text!==f.pnotify_text){if(a.pnotify_insert_brs)a.pnotify_text=a.pnotify_text.replace(/\n/g,"<br />");b.text_container.html(a.pnotify_text).show(200)}b.pnotify_history=a.pnotify_history;a.pnotify_type!=f.pnotify_type&&b.container.toggleClass("ui-state-error ui-state-highlight");if(a.pnotify_notice_icon!=
f.pnotify_notice_icon&&a.pnotify_type=="notice"||a.pnotify_error_icon!=f.pnotify_error_icon&&a.pnotify_type=="error"||a.pnotify_type!=f.pnotify_type){b.container.find("div.ui-pnotify-icon").remove();if(a.pnotify_error_icon&&a.pnotify_type=="error"||a.pnotify_notice_icon)e("<div />",{"class":"ui-pnotify-icon"}).append(e("<span />",{"class":a.pnotify_type=="error"?a.pnotify_error_icon:a.pnotify_notice_icon})).prependTo(b.container)}a.pnotify_width!==f.pnotify_width&&b.animate({width:a.pnotify_width});
a.pnotify_min_height!==f.pnotify_min_height&&b.container.animate({minHeight:a.pnotify_min_height});a.pnotify_opacity!==f.pnotify_opacity&&b.fadeTo(a.pnotify_animate_speed,a.pnotify_opacity);if(a.pnotify_hide)f.pnotify_hide||b.pnotify_queue_remove();else b.pnotify_cancel_remove();b.pnotify_queue_position();return b};b.pnotify_queue_position=function(){m&&clearTimeout(m);m=setTimeout(e.pnotify_position_all,10)};b.pnotify_display=function(){b.parent().length||b.appendTo(k);if(a.pnotify_before_open)if(a.pnotify_before_open(b)===
false)return;b.pnotify_queue_position();if(a.pnotify_animation=="fade"||a.pnotify_animation.effect_in=="fade")b.show().fadeTo(0,0).hide();else a.pnotify_opacity!=1&&b.show().fadeTo(0,a.pnotify_opacity).hide();b.animate_in(function(){a.pnotify_after_open&&a.pnotify_after_open(b);b.pnotify_queue_position();a.pnotify_hide&&b.pnotify_queue_remove()})};b.pnotify_remove=function(){if(b.timer){window.clearTimeout(b.timer);b.timer=null}if(a.pnotify_before_close)if(a.pnotify_before_close(b)===false)return;
b.animate_out(function(){if(a.pnotify_after_close)if(a.pnotify_after_close(b)===false)return;b.pnotify_queue_position();a.pnotify_remove&&b.detach()})};b.animate_in=function(d){c="in";var f;f=typeof a.pnotify_animation.effect_in!="undefined"?a.pnotify_animation.effect_in:a.pnotify_animation;if(f=="none"){b.show();d()}else if(f=="show")b.show(a.pnotify_animate_speed,d);else if(f=="fade")b.show().fadeTo(a.pnotify_animate_speed,a.pnotify_opacity,d);else if(f=="slide")b.slideDown(a.pnotify_animate_speed,
d);else if(typeof f=="function")f("in",d,b);else b.effect&&b.effect(f,{},a.pnotify_animate_speed,d)};b.animate_out=function(d){c="out";var f;f=typeof a.pnotify_animation.effect_out!="undefined"?a.pnotify_animation.effect_out:a.pnotify_animation;if(f=="none"){b.hide();d()}else if(f=="show")b.hide(a.pnotify_animate_speed,d);else if(f=="fade")b.fadeOut(a.pnotify_animate_speed,d);else if(f=="slide")b.slideUp(a.pnotify_animate_speed,d);else if(typeof f=="function")f("out",d,b);else b.effect&&b.effect(f,
{},a.pnotify_animate_speed,d)};b.pnotify_cancel_remove=function(){b.timer&&window.clearTimeout(b.timer)};b.pnotify_queue_remove=function(){b.pnotify_cancel_remove();b.timer=window.setTimeout(function(){b.pnotify_remove()},isNaN(a.pnotify_delay)?0:a.pnotify_delay)};b.closer=e("<div />",{"class":"ui-pnotify-closer",css:{cursor:"pointer",display:"none"},click:function(){b.pnotify_remove();b.closer.hide()}}).append(e("<span />",{"class":"ui-icon ui-icon-circle-close"})).appendTo(b.container);if(a.pnotify_error_icon&&
a.pnotify_type=="error"||a.pnotify_notice_icon)e("<div />",{"class":"ui-pnotify-icon"}).append(e("<span />",{"class":a.pnotify_type=="error"?a.pnotify_error_icon:a.pnotify_notice_icon})).appendTo(b.container);b.title_container=e("<div />",{"class":"ui-pnotify-title",html:a.pnotify_title}).appendTo(b.container);a.pnotify_title===false&&b.title_container.hide();if(a.pnotify_insert_brs&&typeof a.pnotify_text=="string")a.pnotify_text=a.pnotify_text.replace(/\n/g,"<br />");b.text_container=e("<div />",
{"class":"ui-pnotify-text",html:a.pnotify_text}).appendTo(b.container);a.pnotify_text===false&&b.text_container.hide();typeof a.pnotify_width=="string"&&b.css("width",a.pnotify_width);typeof a.pnotify_min_height=="string"&&b.container.css("min-height",a.pnotify_min_height);b.pnotify_history=a.pnotify_history;var h=k.data("pnotify");if(h==null||typeof h!="object")h=[];h=a.pnotify_stack.push=="top"?e.merge([b],h):e.merge(h,[b]);k.data("pnotify",h);a.pnotify_after_init&&a.pnotify_after_init(b);if(a.pnotify_history){var l=
k.data("pnotify_history");if(typeof l=="undefined"){l=e("<div />",{"class":"ui-pnotify-history-container ui-state-default ui-corner-bottom",mouseleave:function(){l.animate({top:"-"+q+"px"},{duration:100,queue:false})}}).append(e("<div />",{"class":"ui-pnotify-history-header",text:"Redisplay"})).append(e("<button />",{"class":"ui-pnotify-history-all ui-state-default ui-corner-all",text:"All",mouseenter:function(){e(this).addClass("ui-state-hover")},mouseleave:function(){e(this).removeClass("ui-state-hover")},
click:function(){e.each(h,function(){this.pnotify_history&&this.pnotify_display&&this.pnotify_display()});return false}})).append(e("<button />",{"class":"ui-pnotify-history-last ui-state-default ui-corner-all",text:"Last",mouseenter:function(){e(this).addClass("ui-state-hover")},mouseleave:function(){e(this).removeClass("ui-state-hover")},click:function(){for(var d=1;!h[h.length-d]||!h[h.length-d].pnotify_history||h[h.length-d].is(":visible");){if(h.length-d===0)return false;d++}d=h[h.length-d];
d.pnotify_display&&d.pnotify_display();return false}})).appendTo(k);q=e("<span />",{"class":"ui-pnotify-history-pulldown ui-icon ui-icon-grip-dotted-horizontal",mouseenter:function(){l.animate({top:"0"},{duration:100,queue:false})}}).appendTo(l).offset().top+2;l.css({top:"-"+q+"px"});k.data("pnotify_history",l)}}a.pnotify_stack.animation=false;b.pnotify_display();return b}});var t=/^on/,u=/^(dbl)?click$|^mouse(move|down|up|over|out|enter|leave)$|^contextmenu$/,v=/^(focus|blur|select|change|reset)$|^key(press|down|up)$/,
w=/^(scroll|resize|(un)?load|abort|error)$/,p=function(g,c){var a;g=g.toLowerCase();if(document.createEvent&&this.dispatchEvent){g=g.replace(t,"");if(g.match(u)){e(this).offset();a=document.createEvent("MouseEvents");a.initMouseEvent(g,c.bubbles,c.cancelable,c.view,c.detail,c.screenX,c.screenY,c.clientX,c.clientY,c.ctrlKey,c.altKey,c.shiftKey,c.metaKey,c.button,c.relatedTarget)}else if(g.match(v)){a=document.createEvent("UIEvents");a.initUIEvent(g,c.bubbles,c.cancelable,c.view,c.detail)}else if(g.match(w)){a=
document.createEvent("HTMLEvents");a.initEvent(g,c.bubbles,c.cancelable)}a&&this.dispatchEvent(a)}else{g.match(t)||(g="on"+g);a=document.createEventObject(c);this.fireEvent(g,a)}};e.pnotify.defaults={pnotify_title:false,pnotify_text:false,pnotify_addclass:"",pnotify_nonblock:false,pnotify_nonblock_opacity:0.2,pnotify_history:true,pnotify_width:"300px",pnotify_min_height:"16px",pnotify_type:"notice",pnotify_notice_icon:"ui-icon ui-icon-info",pnotify_error_icon:"ui-icon ui-icon-alert",pnotify_animation:"fade",
pnotify_animate_speed:"slow",pnotify_opacity:1,pnotify_shadow:false,pnotify_closer:true,pnotify_hide:true,pnotify_delay:8E3,pnotify_mouse_reset:true,pnotify_remove:true,pnotify_insert_brs:true,pnotify_stack:{dir1:"down",dir2:"left",push:"bottom"}}})(jQuery);
