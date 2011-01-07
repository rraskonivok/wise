mrow#{{id}} title="{{type}}"

    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    {{operand}}

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}

    <mi>{{symbol}}</mi>
