{% load custom_tags %}
{% for rule in rules %}
li
    a.ruletoplevel href="javascript:apply_rule('{{rule.1.ref}}',null);"
        {{ rule.0 }}
{% endfor %}
