# Sexp Parser 
# Dmitry Soshnikov <dmitry.soshnikov@gmail.com>
# MIT License

window.parse = (exp) ->

  isSelfEvaluating = (exp) ->
      return true if isNumber(exp) # or isString(exp)
      false

  isNumber = (exp) ->
      not isNaN(Number(exp))

  isString = (exp) ->
      typeof exp is "string"

  isVariable = (exp) ->
      isSymbol exp

  isSymbol = (exp) ->
      /^([a-z-A-Z0-9_$?!+*/=><\-]|>=|<=)+$/.test exp

  exp = exp
    .replace(/;.*$/gm, "")
    .replace(/^\s+|\s+$/g, "")

  return [exp] if isVariable(exp) or exp is ''

  exp = exp
    .replace(/\'\(/g, "(list ") # and replace Lisp's '(1 2 3) with (list 1, 2, 3)
    .replace(/\'([^ ]+)/g, "(quote $1)") # and remove ' to handle 'list
    .replace(/apply\s*(.+)\(list\s*([^)]+)\)/g, "$1 $2") # replace (apply <proc> (list 1 2 3)) with (proc 1 2 3)
    .replace(/\(/g, "[") # replace Lisp's parens...
    .replace(/\)/g, "]") # ... with JS's array squares
    .replace(/\s+/g, ",") # replace spaces in expressions with commas to get real JS arrays

  # Wrap expression(s) with an array to be able
  # execute sequence of statements. We could use wrapping
  # with (begin ...) instead, but for now build JS sequence
  exp = "[#{exp}]"

  # quote the names and build JS arrays of expressions
  expessions = eval(exp.replace(/([^,\[\]0-9]+?(?=(,|\])))/g, "'$1'"))
