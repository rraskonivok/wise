(function(){var root=this;var previousUnderscore=root._;var breaker=typeof StopIteration!=='undefined'?StopIteration:'__break__';var ArrayProto=Array.prototype,ObjProto=Object.prototype;var slice=ArrayProto.slice,unshift=ArrayProto.unshift,toString=ObjProto.toString,hasOwnProperty=ObjProto.hasOwnProperty;var
nativeForEach=ArrayProto.forEach,nativeMap=ArrayProto.map,nativeReduce=ArrayProto.reduce,nativeReduceRight=ArrayProto.reduceRight,nativeFilter=ArrayProto.filter,nativeEvery=ArrayProto.every,nativeSome=ArrayProto.some,nativeIndexOf=ArrayProto.indexOf,nativeLastIndexOf=ArrayProto.lastIndexOf,nativeIsArray=Array.isArray,nativeKeys=Object.keys;var _=function(obj){return new wrapper(obj);};if(typeof exports!=='undefined')exports._=_;root._=_;_.VERSION='1.1.2';var each=_.each=_.forEach=function(obj,iterator,context){try{if(nativeForEach&&obj.forEach===nativeForEach){obj.forEach(iterator,context);}else if(_.isNumber(obj.length)){for(var i=0,l=obj.length;i<l;i++)iterator.call(context,obj[i],i,obj);}else{for(var key in obj){if(hasOwnProperty.call(obj,key))iterator.call(context,obj[key],key,obj);}}}catch(e){if(e!=breaker)throw e;}
return obj;};_.map=function(obj,iterator,context){if(nativeMap&&obj.map===nativeMap)return obj.map(iterator,context);var results=[];each(obj,function(value,index,list){results[results.length]=iterator.call(context,value,index,list);});return results;};_.reduce=_.foldl=_.inject=function(obj,iterator,memo,context){var initial=memo!==void 0;if(nativeReduce&&obj.reduce===nativeReduce){if(context)iterator=_.bind(iterator,context);return initial?obj.reduce(iterator,memo):obj.reduce(iterator);}
each(obj,function(value,index,list){if(!initial&&index===0){memo=value;}else{memo=iterator.call(context,memo,value,index,list);}});return memo;};_.reduceRight=_.foldr=function(obj,iterator,memo,context){if(nativeReduceRight&&obj.reduceRight===nativeReduceRight){if(context)iterator=_.bind(iterator,context);return memo!==void 0?obj.reduceRight(iterator,memo):obj.reduceRight(iterator);}
var reversed=(_.isArray(obj)?obj.slice():_.toArray(obj)).reverse();return _.reduce(reversed,iterator,memo,context);};_.find=_.detect=function(obj,iterator,context){var result;each(obj,function(value,index,list){if(iterator.call(context,value,index,list)){result=value;_.breakLoop();}});return result;};_.filter=_.select=function(obj,iterator,context){if(nativeFilter&&obj.filter===nativeFilter)return obj.filter(iterator,context);var results=[];each(obj,function(value,index,list){if(iterator.call(context,value,index,list))results[results.length]=value;});return results;};_.reject=function(obj,iterator,context){var results=[];each(obj,function(value,index,list){if(!iterator.call(context,value,index,list))results[results.length]=value;});return results;};_.every=_.all=function(obj,iterator,context){iterator=iterator||_.identity;if(nativeEvery&&obj.every===nativeEvery)return obj.every(iterator,context);var result=true;each(obj,function(value,index,list){if(!(result=result&&iterator.call(context,value,index,list)))_.breakLoop();});return result;};_.some=_.any=function(obj,iterator,context){iterator=iterator||_.identity;if(nativeSome&&obj.some===nativeSome)return obj.some(iterator,context);var result=false;each(obj,function(value,index,list){if(result=iterator.call(context,value,index,list))_.breakLoop();});return result;};_.include=_.contains=function(obj,target){if(nativeIndexOf&&obj.indexOf===nativeIndexOf)return obj.indexOf(target)!=-1;var found=false;each(obj,function(value){if(found=value===target)_.breakLoop();});return found;};_.invoke=function(obj,method){var args=slice.call(arguments,2);return _.map(obj,function(value){return(method?value[method]:value).apply(value,args);});};_.pluck=function(obj,key){return _.map(obj,function(value){return value[key];});};_.max=function(obj,iterator,context){if(!iterator&&_.isArray(obj))return Math.max.apply(Math,obj);var result={computed:-Infinity};each(obj,function(value,index,list){var computed=iterator?iterator.call(context,value,index,list):value;computed>=result.computed&&(result={value:value,computed:computed});});return result.value;};_.min=function(obj,iterator,context){if(!iterator&&_.isArray(obj))return Math.min.apply(Math,obj);var result={computed:Infinity};each(obj,function(value,index,list){var computed=iterator?iterator.call(context,value,index,list):value;computed<result.computed&&(result={value:value,computed:computed});});return result.value;};_.sortBy=function(obj,iterator,context){return _.pluck(_.map(obj,function(value,index,list){return{value:value,criteria:iterator.call(context,value,index,list)};}).sort(function(left,right){var a=left.criteria,b=right.criteria;return a<b?-1:a>b?1:0;}),'value');};_.sortedIndex=function(array,obj,iterator){iterator=iterator||_.identity;var low=0,high=array.length;while(low<high){var mid=(low+high)>>1;iterator(array[mid])<iterator(obj)?low=mid+1:high=mid;}
return low;};_.toArray=function(iterable){if(!iterable)return[];if(iterable.toArray)return iterable.toArray();if(_.isArray(iterable))return iterable;if(_.isArguments(iterable))return slice.call(iterable);return _.values(iterable);};_.size=function(obj){return _.toArray(obj).length;};_.first=_.head=function(array,n,guard){return n&&!guard?slice.call(array,0,n):array[0];};_.rest=_.tail=function(array,index,guard){return slice.call(array,_.isUndefined(index)||guard?1:index);};_.last=function(array){return array[array.length-1];};_.compact=function(array){return _.filter(array,function(value){return!!value;});};_.flatten=function(array){return _.reduce(array,function(memo,value){if(_.isArray(value))return memo.concat(_.flatten(value));memo[memo.length]=value;return memo;},[]);};_.without=function(array){var values=slice.call(arguments,1);return _.filter(array,function(value){return!_.include(values,value);});};_.uniq=_.unique=function(array,isSorted){return _.reduce(array,function(memo,el,i){if(0==i||(isSorted===true?_.last(memo)!=el:!_.include(memo,el)))memo[memo.length]=el;return memo;},[]);};_.intersect=function(array){var rest=slice.call(arguments,1);return _.filter(_.uniq(array),function(item){return _.every(rest,function(other){return _.indexOf(other,item)>=0;});});};_.zip=function(){var args=slice.call(arguments);var length=_.max(_.pluck(args,'length'));var results=new Array(length);for(var i=0;i<length;i++)results[i]=_.pluck(args,""+i);return results;};_.indexOf=function(array,item){if(nativeIndexOf&&array.indexOf===nativeIndexOf)return array.indexOf(item);for(var i=0,l=array.length;i<l;i++)if(array[i]===item)return i;return-1;};_.lastIndexOf=function(array,item){if(nativeLastIndexOf&&array.lastIndexOf===nativeLastIndexOf)return array.lastIndexOf(item);var i=array.length;while(i--)if(array[i]===item)return i;return-1;};_.range=function(start,stop,step){var args=slice.call(arguments),solo=args.length<=1,start=solo?0:args[0],stop=solo?args[0]:args[1],step=args[2]||1,len=Math.max(Math.ceil((stop-start)/step),0),idx=0,range=new Array(len);while(idx<len){range[idx++]=start;start+=step;}
return range;};_.bind=function(func,obj){var args=slice.call(arguments,2);return function(){return func.apply(obj||{},args.concat(slice.call(arguments)));};};_.bindAll=function(obj){var funcs=slice.call(arguments,1);if(funcs.length==0)funcs=_.functions(obj);each(funcs,function(f){obj[f]=_.bind(obj[f],obj);});return obj;};_.memoize=function(func,hasher){var memo={};hasher=hasher||_.identity;return function(){var key=hasher.apply(this,arguments);return key in memo?memo[key]:(memo[key]=func.apply(this,arguments));};};_.delay=function(func,wait){var args=slice.call(arguments,2);return setTimeout(function(){return func.apply(func,args);},wait);};_.defer=function(func){return _.delay.apply(_,[func,1].concat(slice.call(arguments,1)));};_.wrap=function(func,wrapper){return function(){var args=[func].concat(slice.call(arguments));return wrapper.apply(wrapper,args);};};_.compose=function(){var funcs=slice.call(arguments);return function(){var args=slice.call(arguments);for(var i=funcs.length-1;i>=0;i--){args=[funcs[i].apply(this,args)];}
return args[0];};};_.keys=nativeKeys||function(obj){if(_.isArray(obj))return _.range(0,obj.length);var keys=[];for(var key in obj)if(hasOwnProperty.call(obj,key))keys[keys.length]=key;return keys;};_.values=function(obj){return _.map(obj,_.identity);};_.functions=_.methods=function(obj){return _.filter(_.keys(obj),function(key){return _.isFunction(obj[key]);}).sort();};_.extend=function(obj){each(slice.call(arguments,1),function(source){for(var prop in source)obj[prop]=source[prop];});return obj;};_.clone=function(obj){return _.isArray(obj)?obj.slice():_.extend({},obj);};_.tap=function(obj,interceptor){interceptor(obj);return obj;};_.isEqual=function(a,b){if(a===b)return true;var atype=typeof(a),btype=typeof(b);if(atype!=btype)return false;if(a==b)return true;if((!a&&b)||(a&&!b))return false;if(a.isEqual)return a.isEqual(b);if(_.isDate(a)&&_.isDate(b))return a.getTime()===b.getTime();if(_.isNaN(a)&&_.isNaN(b))return false;if(_.isRegExp(a)&&_.isRegExp(b))
return a.source===b.source&&a.global===b.global&&a.ignoreCase===b.ignoreCase&&a.multiline===b.multiline;if(atype!=='object')return false;if(a.length&&(a.length!==b.length))return false;var aKeys=_.keys(a),bKeys=_.keys(b);if(aKeys.length!=bKeys.length)return false;for(var key in a)if(!(key in b)||!_.isEqual(a[key],b[key]))return false;return true;};_.isEmpty=function(obj){if(_.isArray(obj)||_.isString(obj))return obj.length===0;for(var key in obj)if(hasOwnProperty.call(obj,key))return false;return true;};_.isElement=function(obj){return!!(obj&&obj.nodeType==1);};_.isArray=nativeIsArray||function(obj){return!!(obj&&obj.concat&&obj.unshift&&!obj.callee);};_.isArguments=function(obj){return!!(obj&&obj.callee);};_.isFunction=function(obj){return!!(obj&&obj.constructor&&obj.call&&obj.apply);};_.isString=function(obj){return!!(obj===''||(obj&&obj.charCodeAt&&obj.substr));};_.isNumber=function(obj){return(obj===+obj)||(toString.call(obj)==='[object Number]');};_.isBoolean=function(obj){return obj===true||obj===false;};_.isDate=function(obj){return!!(obj&&obj.getTimezoneOffset&&obj.setUTCFullYear);};_.isRegExp=function(obj){return!!(obj&&obj.test&&obj.exec&&(obj.ignoreCase||obj.ignoreCase===false));};_.isNaN=function(obj){return _.isNumber(obj)&&isNaN(obj);};_.isNull=function(obj){return obj===null;};_.isUndefined=function(obj){return typeof obj=='undefined';};_.noConflict=function(){root._=previousUnderscore;return this;};_.identity=function(value){return value;};_.times=function(n,iterator,context){for(var i=0;i<n;i++)iterator.call(context,i);};_.breakLoop=function(){throw breaker;};_.mixin=function(obj){each(_.functions(obj),function(name){addToWrapper(name,_[name]=obj[name]);});};var idCounter=0;_.uniqueId=function(prefix){var id=idCounter++;return prefix?prefix+id:id;};_.setCounter=function(start){idCounter=start;}
_.getCounter=function(start){return idCounter;}
_.resetCounter=function(start){idCounter=0;}
_.templateSettings={evaluate:/<%([\s\S]+?)%>/g,interpolate:/<%=([\s\S]+?)%>/g};_.template=function(str,data){var c=_.templateSettings;var tmpl='var __p=[],print=function(){__p.push.apply(__p,arguments);};'+'with(obj||{}){__p.push(\''+
str.replace(/'/g,"\\'").replace(c.interpolate,function(match,code){return"',"+code.replace(/\\'/g,"'")+",'";}).replace(c.evaluate||null,function(match,code){return"');"+code.replace(/\\'/g,"'").replace(/[\r\n\t]/g,' ')+"__p.push('";}).replace(/\r/g,'\\r').replace(/\n/g,'\\n').replace(/\t/g,'\\t')
+"');}return __p.join('');";var func=new Function('obj',tmpl);return data?func(data):func;};var wrapper=function(obj){this._wrapped=obj;};_.prototype=wrapper.prototype;var result=function(obj,chain){return chain?_(obj).chain():obj;};var addToWrapper=function(name,func){wrapper.prototype[name]=function(){var args=slice.call(arguments);unshift.call(args,this._wrapped);return result(func.apply(_,args),this._chain);};};_.mixin(_);each(['pop','push','reverse','shift','sort','splice','unshift'],function(name){var method=ArrayProto[name];wrapper.prototype[name]=function(){method.apply(this._wrapped,arguments);return result(this._wrapped,this._chain);};});each(['concat','join','slice'],function(name){var method=ArrayProto[name];wrapper.prototype[name]=function(){return result(method.apply(this._wrapped,arguments),this._chain);};});wrapper.prototype.chain=function(){this._chain=true;return this;};wrapper.prototype.value=function(){return this._wrapped;};})();