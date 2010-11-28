{% load custom_tags %}
div#rules_palette.palette style="display:none"
    ul.navigation
        {% for title, rules in rulesets.items %}
            a.panel_category href="#"
                {{ title }}

            li.panel_frame
                {% for rule in rules %}
                    a.ruletoplevel href="javascript:apply_rule('{{rule.1.pure}}',null);" title="{{rule.1.desc}}"
                        {{rule.0}}
                {% endfor %}
        {% endfor %}
