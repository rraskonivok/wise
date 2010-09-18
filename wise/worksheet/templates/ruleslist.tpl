{% load custom_tags %}
div#rules_palette style="display:none"
    ul.navigation
        {% for title, rules in rulesets.items %}
            a.panel_category href="#"
                {{ title }}

            {% for rule in rules %}
            li.panel_frame
                a.ruletoplevel href="javascript:apply_rule('{{rule.1.ref}}',null);"
                    {{rule.0}}
            {% endfor %}
        {% endfor %}
