#{{id}}.term.{{class}} title="{{type}}"

    {% if parenthesis %}
    .pnths.left
        (
    {% endif %}

    {{operand}}

    {% if parenthesis %}
    .pnths.right
        )
    {% endif %}

    .operator
        $${{symbol}}$$
