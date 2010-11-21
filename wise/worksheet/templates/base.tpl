{% load media %}

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Wise ( {{title|title}} ) </title>

 {% include_media 'jqueryui_stylesheets.css' %}

<!--  <link rel="stylesheet" type="text/css" href="/static/css/math.css" />
  <link rel="stylesheet" type="text/css" href="/static/ui/ui.css" />
  <link rel="stylesheet" href="/static/css/base.css" type="text/css" media="screen" />
  <link rel="stylesheet" id="current-theme" href="/static/css/themes/default/style.css" type="text/css" media="screen" />
  <link rel="stylesheet" type="text/css" href="/static/css/worksheet.css" />
  -->

 {% include_media 'base.js' %}

 {% block includes %}
 {% endblock %}

</head>
<body>
  <div id="container">

    {% block header %}
    <div id="header">
      <h1><a href="/">Wise</a></h1>
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
    </div>
    {% endblock %}

    <div id="wrapper" class="wat-cf">
      <div id="main">
        {% block main %}
        {% endblock %}
      </div>
      <div id="sidebar">
        {% block sidebar %}
        {% endblock %}
      </div>
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

