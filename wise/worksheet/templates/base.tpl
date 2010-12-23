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
  <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />
  <meta http-equiv="Content-Language" content="en" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <meta http-equiv="Content-Script-Type" content="text/javascript" />

 {% load_bundle "base_js" %}
 {% load_bundle "base_css" %}

 {% block includes %}
 {% endblock %}

 {% block globals %}
 {% endblock %}

</head>
<body>

  <div id="container">

    {% block header %}
    <div id="header">
      <h1><a href="/">Wise</a></h1>

      {% if user.is_authenticated %}
      <div id="user-navigation">
        <ul class="wat-cf">
          <li><a href="#">Profile</a></li>
          <li><a href="#">Settings</a></li>
          <li><a class="logout" href="/accounts/logout">Logout</a></li>
        </ul>
      </div>
      <div id="main-navigation">
        <ul class="wat-cf">
          {% block main-navigation %}
          {% endblock %}
        </ul>
      </div>
      {% endif %}
    </div>
    {% endblock %}

    <div id="wrapper" class="wat-cf">
      <div id="main">
        {% block main %}
        {% endblock %}

        {% block content %}
        {% endblock %}
      </div>
        {% block sidebar %}
        {% endblock %}
      <div id="box">
        {% block box %}
        {% endblock %}
      </div>
    </div>
  </div>
  {% block inline-script %}
  {% endblock %}
</body>
</html>

