#{{id}}.container.{{class}} title="{{type}}"

    .operator
        $${{symbol}}$$

    {% if parenthesis %}
    .pnths.left
        (
    {% endif %}

    {{operand}}

    sup
        {{symbol1}}

    {% if parenthesis %}
    .pnths.right
        )
    {% endif %}
