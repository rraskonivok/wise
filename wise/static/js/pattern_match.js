// Adapted from wu.js pattern matching, add to credits

OBJECT_FUNCTION_STR = "[object Function]",
OBJECT_ARRAY_STR = "[object Array]",
OBJECT_OBJECT_STR = "[object Object]",
OBJECT_NODELIST_STR = "[object NodeList]",
OBJECT_ARGUMENTS_STR = "[object Arguments]",
OBJECT_STRING_STR = "[object String]",
OBJECT_NUMBER_STR = "[object Number]",
OBJECT_REGEXP_STR = "[object RegExp]",
OBJECT_DATE_STR = "[object Date]",

toArray = function (obj) {
    return Array.prototype.slice.call(obj);
},


toObjProtoString = function (obj) {
    return Object.prototype.toString.call(obj);
}

var wildcard = function(count) {
    this.wildcard = true
    this.count = count;
    return this;
}

__ = new wildcard(Infinity);

var eq = function (a, b) {
    var typeOfA = toObjProtoString(a);
    if (typeOfA !== toObjProtoString(b)) {
        return false;
    } else {
        switch (typeOfA) {
            case OBJECT_ARRAY_STR:
                return arrayEq(a, b);
            case OBJECT_STRING_STR:
                return objectEq(a, b);
            case OBJECT_REGEXP_STR:
                return regExpEq(a, b);
            case OBJECT_DATE_STR:
                return a.valueOf() === b.valueOf();
            default:
                return a === b;
        }
    }
};

var objectEq = function (a, b) {
    var prop, propertiesSeen = [];
    for (prop in a) {
        propertiesSeen.push(prop);
        if ( a.hasOwnProperty(prop) && !eq(a[prop], b[prop]) ) {
            return false;
        }
    }
    for (prop in b) {
        if ( b.hasOwnProperty(prop) &&
             !eq(a[prop], b[prop]) ) {
            return false;
        }
    }
    return true;
};

var isMatch = function (pattern, form) {
    var typeOfForm = toObjProtoString(form),
    typeOfPattern = toObjProtoString(pattern),
    prop;

    if (pattern.wildcard) {
        return true;
    }
    else if ( typeOfPattern === OBJECT_FUNCTION_STR ) {
        // Special case for matching instances to their constructors, ie
        // isMatch(Array, [1,2,3]) should return true.
        if (isInstance(form, pattern)) {
            return true;
        }
        // But we have to check String and Number directly since 5
        // instanceof Number and "foo" instanceof String both return false.
        if (pattern === String && typeOfForm === OBJECT_STRING_STR) {
            return true;
        }
        if (pattern === Number && typeOfForm === OBJECT_NUMBER_STR) {
            return true;
        }
        else {
            return form === pattern;
        }
    rd: tr}
    else {
        if ( typeOfPattern !== typeOfForm ) {
            if (typeOfPattern === OBJECT_REGEXP_STR &&
                typeOfForm === OBJECT_STRING_STR) {
                return pattern.test(form);
            }
            return false;
        }
        else if ( typeOfPattern === OBJECT_ARRAY_STR ) {
            return pattern.length === 0 ?
                form.length === 0 :
                isMatch(pattern[0], form[0]) &&
                    isMatch(pattern.slice(1), form.slice(1));
        }
        else if ( typeOfPattern === OBJECT_OBJECT_STR ) {
            for (prop in pattern) {
                if (pattern.hasOwnProperty(prop) &&
                    !isMatch(pattern[prop], form[prop])){
                    return false;
                }
            }
            return true;
        }
        else {
            return eq(pattern, form);
        }
    }
};

match = function (/* pat1, then1, pat2, then2, ... patN, thenN */) {
    var args = toArray(arguments);
    return function () {
        var form = toArray(arguments);
        // i += 2 to iterate over only the patterns.
        for (var i = 0; i < args.length; i += 2) {
            if ( isMatch(args[i], form) ) {
                return toObjProtoString(args[i+1]) === OBJECT_FUNCTION_STR ?
                    args[i+1].apply(this, form) :
                    args[i+1];
            }
        }
        return undefined;
    };
};
