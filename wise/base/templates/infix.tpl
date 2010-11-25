{% load custom_tags %}

#{{id}}.container.{{class}} title="{{type}}"

    .pnths.left {% conditional_display parenthesis %} 
        (

    {% for o in operand %}
    {{ o }}

        {% if not forloop.last %}
        .infix.sugar
            $${{symbol}}$$
        {% endif %}

    {% endfor %}

    .pnths.right {% conditional_display parenthesis %} 
        )
