{% load custom_tags %}

mrow
    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    mfrac#{{id}} title="{{type}}"
        {{num}}
        {{den}}

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
