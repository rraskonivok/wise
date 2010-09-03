{% load custom_tags %}
ul
    {% for rule in rules %}
    li
        a.ruletoplevel href="javascript:apply_rule('{{rule.1.ref}}',null);"
            {{ rule.0 }}
    {% endfor %}
