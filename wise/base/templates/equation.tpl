tr#{{id}}.equation math="{{math}}" math-type="{{classname}}" toplevel="true"
    td
        button.ui-icon.ui-icon-triangle-1-w onclick="select_term(get_lhs(this))"
            {{lhs_id}}

        button.ui-icon.ui-icon-triangle-2-e-w onclick="select_term(get_equation(this))"
            {{id}}

        button.ui-icon.ui-icon-triangle-1-e onclick="select_term(get_rhs(this))"
            {{rhs_id}}

    td
        {{lhs}}

    td.equalsign
       $${{symbol}}$$

    td
        {{rhs}}

    td.guard 
        {{guard}}

    td.annotation
        div contenteditable=true
            {{annotation}}
