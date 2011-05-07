{% load bundler_tags %}
{% load html %}
{% if xhtml %}
{% doctype "xhtmlmath" %}
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
{% else %}
{% doctype "html5" %}
<html>
{% endif %}

<head>
  <title>Wise ( {{title|title}} ) </title>

  {% if xhtml %}
  <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />
  {% endif %}

  <meta http-equiv="Content-Language" content="en" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta http-equiv="Content-Script-Type" content="text/javascript" />

  {% load_bundle "base_js" %}
  {% load_bundle "base_css" %}

  {% block includes %}
  {% endblock %}

  {% block inline_css %}
  {% endblock %}

  {% block globals %}
  {% endblock %}

</head>
<body>
    {% block loading %}
    <div id="progressbar"></div>
    {% endblock %}

    {% block header %}
        <div id="headerbar">
            <a href="{% url home %}" class="headernav">My Worksheets</a> 
            <span class="headerright">
            {% if user.is_authenticated %}
                <span class="headernav">
                <b><a href="{% url profile %}">{{ user.username }}</a></b>
                </span>
                {% if user.is_staff %}
                <span class="headernav">
                    <a href="{% url admin:index %}">Admin</a>
                </span>
                {% endif %}
                <span class="headernav">
                <a class="logout" href="{%url auth_logout %}">Logout</a>
                </span>
            {% endif %}
            </span>
        </div>
    {% endblock %}

    <!-- Partial Page Content -->
    <div id="box" class="hidden">
        {% block box %}
        {% endblock %}
    </div>

    <!-- Full Page Content -->
    <div id="container" class="hidden">
        {% block main %}
        {% endblock %}
    </div>

  {% block inline_js %}
  {% endblock %}

  {% block analytics %}
  {% endblock %}
</body>
</html>

