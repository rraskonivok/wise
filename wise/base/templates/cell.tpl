<div class="cell" id="cell{{index}}">
    <div class="cellbuttons">
    <span onclick="javascript:new_line('eq','cell{{index}}');" class="ui-icon ui-icon-circle-plus"></span>
    </div>
        {% for eq in eqs %}
            {{ eq }}
        {% endfor %}
</div>
