mrow#{{id}} title="{{type}}"

    <mo>{{symbol}}</mo>

    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    {% for o in operand %}
        {{ o }}
    {% endfor %}

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
