mrow#{{id}} title="{{type}}"

    <mi>{{symbol}}</mi>

    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    {{operand}}

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
