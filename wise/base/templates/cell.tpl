div#cell{{index}}.cell
    div.assumptions
        {% for as in assms %}
            {{ as }}
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

        {% for eq in eqs %}
            {{ eq }}
        {% endfor %}
