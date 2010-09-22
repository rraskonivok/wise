<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}">
    <span class="operator" math-type="operator" math-meta-class="operator" group="{{id}}" title="{{type}}" >
        {% if notex %}
        {{symbol}}
        {% else %}
        $${{symbol}}$$
        {% endif %}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
        (
    </span>
    {% endif %}

    <span class="">
    {{operand}}
    </span>

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
        )
    </span>
    {% endif %}

</span>
