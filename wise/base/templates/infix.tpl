#{{id}}.{{class}}.container math-meta-class="term"  math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}"
    {% if parenthesis %}
    .ui-state-disabled.pnths.left
       &Ograve;
    {% endif %}

    {% for o in operand %}
    {{ o }}
    {% if not forloop.last %}
    .ui-state-disabled.infix math-type="times" math-meta-class="sugar"
        $${{symbol}}$$
    {% endif %}
    {% endfor %}

    {% if parenthesis %}

    .ui-state-disabled.pnths.right
       &Oacute;

    {% endif %}

{{jscript}}
