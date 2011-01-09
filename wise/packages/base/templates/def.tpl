<tr id="{{id}}" class="equation" math="{{math}}"
math-type="{{classname}}" toplevel="true" data-confluent="{{confluent}}" data-public="{{public}}">

<td>
    <button class="ui-icon ui-icon-transferthick-e-w"
    onclick="apply_transform('ReverseDef',get_equation(this))">{{lhs_id}}</button>
    <button class="ui-icon ui-icon-arrow-4" onclick="select_equation('{{id}}')">{{id}}</button>
    <button class="confluence 
    {% if confluent %} 
    ui-icon ui-icon-bullet
    {% else %}
    ui-icon ui-icon-radio-off
    {% endif %}
    " onclick="toggle_confluence(get_equation(this))">{{id}}</button>
</td>
<td>{{lhs}}</td>
<td><span class="equalsign">$${{symbol}}$$</span></td>
<td>{{rhs}}</td>
<td class="guard">{{guard}}</td>
<td class="annotation"><div contenteditable=true>{{annotation}}</div></td>

</tr>
