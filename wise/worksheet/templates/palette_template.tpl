<div id="math_palette">
    <ul class="navigation">
    {% for panel in panels %}
        <a href="#" class="panel_category">{{ panel.name }}</a>
        <li class="panel_frame" style="display:none">
            {{ panel.html }}
        </li>
        <hr/>
    {% endfor %}
    </ul>
</div>
