tr#{{id}}.equation math-type="{{classname}}" toplevel="true"
    td
        button.ui-icon.ui-icon-triangle-1-w onclick="select_lhs('{{id}}')"
            {{lhs_id}}
        button.ui-icon.ui-icon-triangle-2-e-w onclick="select_equation('{{id}}')"
            {{id}}
        button.ui-icon.ui-icon-triangle-1-e onclick="select_rhs('{{id}}')"
            {{rhs_id}}
    td
        {{lhs}}
    td.equalsign
       $${{symbol}}$$
    td
        {{rhs}}
    td.guard 
        {{guard}}
    td.annotation.last 
        div contenteditable=true
            {{annotation}}
