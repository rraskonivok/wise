#{{id}}.{{class}}.container math-meta-class="term"  math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}"

    {% if parenthesis %}
    <span class="ui-state-disabled pnths left">
        (
    </span>
    {% endif %}

    {% for o in operand %}
    {{ o }}
    {% if not forloop.last %}
    .ui-state-disabled.infix math-type="times" math-meta-class="sugar"
        {% if notex %}
        {{symbol}}
        {% else %}
        $${{symbol}}$$
        {% endif %}
    {% endif %}
    {% endfor %}

    {% if parenthesis %}
    <span class="ui-state-disabled pnths right">
        )
    </span>
    {% endif %}

{{jscript}}
