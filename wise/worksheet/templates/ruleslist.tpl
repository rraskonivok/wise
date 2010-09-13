{% load custom_tags %}
{% for rule in rules %}
li.panel_category
    a.ruletoplevel href="javascript:apply_rule('{{rule.1.ref}}',null);"
        {{ rule.0 }}
{% endfor %}
