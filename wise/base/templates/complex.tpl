#{{id}}.container.{{class}} title="{{type}}"

    {% if parenthesis %}
    .pnths.left
        (
    {% endif %}

    {{ re }}

    .infix.sugar
        $$+$$

    {{ im }}

    .texdecoration.sugar
        $$i$$

    {% if parenthesis %}
    .pnths.right
        )
    {% endif %}
