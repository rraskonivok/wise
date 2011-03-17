mrow#{{id}} title="{{type}}"
    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    {{ re }}

    <mo>+</mo>

    {{ im }}

    <mi>ⅈ</mi>

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
