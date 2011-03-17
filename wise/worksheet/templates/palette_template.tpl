<div id="math_palette" class="palette">
    <ul class="navigation">
    {% for panel in panels %}
        <li class="panel_category noselect">{{ panel.name }}</li>
        <li class="panel_frame" style="display:none">
            {{ panel.html }}
        </li>
    {% endfor %}
    </ul>
</div>
