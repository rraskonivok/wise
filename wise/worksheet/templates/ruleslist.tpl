{% load custom_tags %}
ul
    {% for rule in rules %}
    li
        a.ruletoplevel href="javascript:apply_rule({{rule.0.id}},null);"
            {{ rule.0.name }}

        a.expand
            [+]

        ul
            {% for subrule in rule.1 %}
                li
                    a href="javascript:apply_rule({{rule.0.id}},{{subrule.id}});"
                        {{ subrule.annotation|brak2tex }}
            {% endfor %}
    {% endfor %}
