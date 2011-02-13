<mrow id="{{id}}">
  <mmultiscripts>
    <mrow>
    {% if parenthesis %}
    <mo stretchy="true">(</mo>
    {% endif %}
    <mi>{{base}}</mi>
    {% if parenthesis %}
    <mo stretchy="true">)</mo>
    {% endif %}
    </mrow>
    {{co}}
    <mprescripts></mprescripts>
    {{cv}}
  </mmultiscripts>
</mrow>
