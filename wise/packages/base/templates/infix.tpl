{% load custom_tags %}

<mrow id="{{id}}">
    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    {% for o in operand %}
    {{ o }}
        {% if not forloop.last %}
        <mo>{{symbol|safe}}</mo>
        {% endif %}
    {% endfor %}

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
</mrow>
