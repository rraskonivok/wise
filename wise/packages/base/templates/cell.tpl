div#cell{{index}}.cell

    div.node-outline
        PASS

    div.equations

        {% for ex in expressions %}
            {{ ex|safe }}
        {% endfor %}

    div.insertion_toolbar
        PASS

    .add.ui-icon.ui-icon-circle-plus
        PASS

    .del.ui-icon.ui-icon-circle-minus
        PASS
