table style="width: 100%"

    {% for symbol in symbols %}
    tr
        td
            {{ symbol.0 }}

        td
            {{ symbol.1 }}
    {% endfor %}
