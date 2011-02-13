<table>
<tr>
{% for button in buttons %}
  <td>
  <span title="{{ button.tooltip|escape }}" class="uniform_button" onclick="subs('{{ button.math }}');">
  {{ button.mathml|safe }}
  </span>
  </td>
  {% if forloop.counter|divisibleby:"5" %}
    </tr><tr>
  {% endif %}
{% endfor %}
</tr>
</table>
