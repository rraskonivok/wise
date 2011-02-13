mrow#{{id}} title="{{type}}"
    <mo>{{symbol}}</mo>
    <mo stretch="true">(</mo>

    {% for o in operand %}
    {{ o }}

    {% if not forloop.last %}
    <mo>,</mo>
    {% endif %}

    {% endfor %}

    <mo stretch="true">)</mo>
