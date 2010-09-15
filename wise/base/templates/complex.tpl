
#{{id}}.{{class}}.container math-meta-class="term"  math="{{math}}" math-type="{{type}}" math-meta-class="term" group="{{group}}"
    {% if parenthesis %}
    .ui-state-disabled.pnths.left
       &Ograve;
    {% endif %}

    {{ re }}

    .ui-state-disabled.infix math-type="plus" math-meta-class="sugar"
        $$+$$

    {{ im }}

    .ui-state-disabled.texdecoration math-type="complex" math-meta-class="sugar"
        $$i$$

    {% if parenthesis %}
    .ui-state-disabled.pnths.right
       &Oacute;

    {% endif %}
