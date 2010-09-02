{% for panel in panels %}
    <h3><a href="#">{{ panel.name }}</a></h3>
    <div>
        {{ panel.html }}
    </div>
{% endfor %}
