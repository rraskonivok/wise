mrow#{{id}}
    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    msup
        {{base}}
        {{exponent}}

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
