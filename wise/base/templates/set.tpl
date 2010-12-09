mrow#{{id}} title="{{type}}"
    <mo>{</mo>

    {% for o in operand %}
    {{ o }}

    {% if not forloop.last %}
    <mo>,</mo>
    {% endif %}

    {% endfor %}

    <mo>}</mo>
