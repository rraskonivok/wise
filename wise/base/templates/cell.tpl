div#cell{{index}}.cell

    div.content-node-outline
        PASS

    div.assumptions
        {% for asm in assumptions %}
            {{ asm }}
        {% endfor %}
        
    div.equations

        div.cellbuttons
            .hide.ui-icon.ui-icon-triangle-1-n
                PASS
            .add.ui-icon.ui-icon-circle-plus
                PASS
            .del.ui-icon.ui-icon-circle-minus
                PASS
            .save.ui-icon.ui-icon-disk
                PASS

        {% for ex in expressions %}
            {{ ex }}
        {% endfor %}
