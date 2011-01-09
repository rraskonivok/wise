<tr id="{{id}}" class="equation" math="{{math}}"
math-type="{{classname}}" toplevel="true" data-confluent="{{confluent}}" data-public="{{public}}">

<td>
    <button class="ui-icon ui-icon-extlink" onclick="apply_transform('base/GenFunc',[selection.nth(0),selection.nth(1)])">{{lhs_id}}</button>
    <button class="ui-icon ui-icon-arrow-4" onclick="select_equation('{{id}}')">{{id}}</button>
    <button class="confluence 
    {% if confluent %} 
    ui-icon ui-icon-bullet
    {% else %}
    ui-icon ui-icon-radio-off
    {% endif %}
    " onclick="toggle_confluence(get_equation(this))">{{id}}</button>
</td>
<td>{{head}}</td>
<td><span class="equalsign">$$:$$</span></td>
<td>{{lhs}}</td>
<td><span class="equalsign">$$\rightarrow$$</span></td>
<td>{{rhs}}</td>
<td class="guard">{{guard}}</td>
<td class="annotation"><div contenteditable=true>{{annotation}}</div></td>

</tr>
