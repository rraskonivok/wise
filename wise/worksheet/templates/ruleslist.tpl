div#rules
    ul#rulelist.navigation
        {% for title, rules in rulesets.items %}
            li.panel_category.noselect
                {{ title }}

            li.panel_frame
                {% for rule in rules %}
                    li.rule
                        a href="#" onclick="javascript:apply_rule('{{rule.1.pure}}',null);" title="{{rule.1.desc}}"
                            {{rule.0}}
                {% endfor %}
        {% endfor %}
