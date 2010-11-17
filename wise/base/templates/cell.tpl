<div class="cell" id="cell{{index}}">
    <div class="cellbuttons">
    <span onclick="javascript:new_line('eq','cell{{index}}');" class="ui-icon ui-icon-circle-plus"></span>
    <span onclick="javascript:del_cell('eq','cell{{index}}');" class="ui-icon ui-icon-circle-minus"></span>
    <span onclick="javascript:save_cell('eq','cell{{index}}');" class="ui-icon ui-icon-disk"></span>
    </div>
        {% for eq in eqs %}
            {{ eq }}
        {% endfor %}
</div>
