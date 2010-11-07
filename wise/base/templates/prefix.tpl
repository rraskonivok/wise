<span id="{{id}}" math-meta-class="term" class="container {{class}}{{sensitive}}" math-meta-class="term">
    <span class="operator" math-type="operator" math-meta-class="operator" >
        $${{symbol}}$$
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
