#{{id}}.{{class}}.container math-meta-class="term" math-type="{{type}}" math-meta-class="term"

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
        (
    </span>
    {% endif %}

    {% for o in operand %}
    {{ o }}
    {% if not forloop.last %}
    .ui-state-disabled.infix math-type="times" math-meta-class="sugar"
        $${{symbol}}$$
    {% endif %}
    {% endfor %}

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
        )
    </span>
    {% endif %}

{{jscript}}
