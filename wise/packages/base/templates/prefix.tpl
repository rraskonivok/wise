mrow#{{id}} title="{{type}}"

    <mo>{{symbol}}</mo>

    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    {{operand}}

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
