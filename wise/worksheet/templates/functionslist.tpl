table style="width: 100%"
    {% for symbol in symbols%}
    tr
        td
            {{ function.0 }}
        td
            {{ function.1 }}
    {% endfor %}
