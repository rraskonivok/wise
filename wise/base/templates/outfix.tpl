    <span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">

    {{symbol1}}

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
       &Ograve;
    </span>
    {% endif %}

    <span class="parenthesis">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
       &Oacute;
    </span>
    {% endif %}

    {{symbol2}}

    </span>
