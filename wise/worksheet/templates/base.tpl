<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Wise ( {{title|title}} ) </title>

  <link rel="stylesheet" type="text/css" href="/static/css/math.css" />
  <link rel="stylesheet" type="text/css" href="/static/ui/ui.css" />
  <link rel="stylesheet" href="/static/css/base.css" type="text/css" media="screen" />
  <link rel="stylesheet" id="current-theme" href="/static/css/themes/default/style.css" type="text/css" media="screen" />
  <link rel="stylesheet" type="text/css" href="/static/css/worksheet.css" />

  <!-- Load jQuery -->
 <script src="/static/js/jquery.js" type="text/javascript"></script>
 <script src="/static/js/jquery-ui.js" type="text/javascript"></script>
 <script src="/static/js/dimensions.js" type="text/javascript"></script>
 <script src="/static/js/tooltip.js" type="text/javascript"></script>

  <!-- ajaxmanager.js -->
 <script src="/static/js/jquery.ajaxmanager.js"></script> 

  <!-- underscore.js -->
 <script src="/static/js/underscore.js" type="text/javascript"></script>

  <!-- underscore.js -->
 <script src="/static/js/json2.js" type="text/javascript"></script>

  <!-- backbone.js / depends on underscore.js and json2.js -->
 <script src="/static/js/backbone.js" type="text/javascript"></script>

  <!-- Notification Plugin -->
 <script src="/static/js/pnotify.js" type="text/javascript"></script>

 <!-- Hotkeys Plugin -->
 <script src="/static/js/keys.js" type="text/javascript"></script>

</head>
<body>
  <div id="container">
    <div id="header">
      <h1><a href="/">Wise</a></h1>
      <div id="user-navigation">
        <ul class="wat-cf">
          <li><a href="#">Profile</a></li>
          <li><a href="#">Settings</a></li>
          <li><a class="logout" href="#">Logout</a></li>
        </ul>
      </div>
      <div id="main-navigation">
        <ul class="wat-cf">
          {% block main-navigation %}
          {% endblock %}
        </ul>
      </div>
    </div>
    <div id="wrapper" class="wat-cf">
      <div id="main">
        {% block main %}
        {% endblock %}
      </div>
      <div id="sidebar">
        <div class="block">
          <h3>Simple Block</h3>
          <div class="content">
            <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>

