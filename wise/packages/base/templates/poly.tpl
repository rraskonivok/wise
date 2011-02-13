<mrow id="{{id}}">
    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    <mo>Poly</mo>
    <mo stretchy="false">[</mo>
    <mo>{{var}}</mo>
    <mo stretchy="false">]</mo>

    <mo stretchy="true">(</mo>

    {% for o in operand %}
    {{ o }}
        {% if not forloop.last %}
        <mo>{{symbol|safe}}</mo>
        {% endif %}
    {% endfor %}

    <mo stretchy="true">)</mo>

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
</mrow>
