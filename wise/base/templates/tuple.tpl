#{{id}}.container.{{class}} title="{{type}}"

    {% if parenthesis %}
    .pnths.left
        (
    {% endif %}

    {% for o in operand %}
    {{ o }}

        {% if not forloop.last %}
        .infix.sugar
            $${{symbol}}$$
        {% endif %}

    {% endfor %}

    {% if parenthesis %}
    .pnths.right
        )
    {% endif %}
