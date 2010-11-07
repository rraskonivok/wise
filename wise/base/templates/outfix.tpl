    <span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" title="{{type}}" math-meta-class="term" 

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
