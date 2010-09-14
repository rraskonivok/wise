<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="{{class}}">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

</span>