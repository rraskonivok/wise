mrow#{{id}}
    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}

    <mfrac title="{{type}}">
        <mo>d</mo>
        <mrow>
            <mo>d</mo>
            {{variable}}
        </mrow>
    </mfrac>
    {{operand}}

    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
