{% load bundler_tags %}
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN" 
               "http://www.w3.org/Math/DTD/mathml2/xhtml-math11-f.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"> 
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

