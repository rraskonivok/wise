#{{id}}.container.{{class}} title="{{type}}"

    .operator
        $${{symbol}}$$

    {% if parenthesis %}
    .pnths.left
        (
    {% endif %}

    {{operand}}

    {% if parenthesis %}
    .pnths.right
        )
    {% endif %}
