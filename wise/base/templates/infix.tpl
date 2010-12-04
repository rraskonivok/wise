{% load custom_tags %}

<mrow id="{{id}}">
    {% for o in operand %}
    {{ o }}

        {% if not forloop.last %}
        <mo>{{symbol|safe}}</mo>
        {% endif %}

    {% endfor %}
</mrow>
