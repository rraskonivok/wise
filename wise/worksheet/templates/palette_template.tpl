<div id="math_palette">
    <ul class="navigation">
    <a href="#">{{ panel.name }}</a>
    {% for panel in panels %}
        <li>
            {{ panel.html }}
        </li>
    {% endfor %}
    </ul>
</div>
