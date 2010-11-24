from settings import MEDIA_ROOT, MEDIA_URL

MEDIA_BUNDLES = (
    # Base stylesheet (web-app-theme) and jQuery ui stylesheets
    {"type": "css",
     "name": "base_css",
     "path": MEDIA_ROOT,
     "url": MEDIA_URL,
     "minify": False,
     "files": (
        'css/base.css',
        'css/themes/default/style.css',
        'ui/ui.css',
     )},

    # Worksheet stylesheets
    {"type": "css",
     "name": "worksheet_css",
     "path": MEDIA_ROOT + "css/",
     "url": MEDIA_URL + "css/",
     "minify": False,
     "files": (
        'math.css',
        'worksheet.css',
     )},

    # Base Javascript libraries, mostly jQuery plugins, backbone
    # and underscore
    {"type": "javascript",
     "name": "base_js",
     "path": MEDIA_ROOT + "js/",
     "url": MEDIA_URL + "js/",
     "minify": False,
     "files": (
        'jquery.js',
        'jquery-ui.js',
        'dimensions.js',
        'json2.js',
        'underscore.js',
        'backbone.js',
        'qtip.js',
        'pnotify.js',
        'keys.js',
        'jquery.ajaxmanager.js',
     )},

    {"type": "javascript",
     "name": "worksheet_js",
     "path": MEDIA_ROOT + "js/",
     "url": MEDIA_URL + "js/",
     "minify": False,
     "files": (
        'worksheet.js',
        'interactions.js',
        'worksheet_ui.js',
        'editable.js',
        'worksheet_managers.js',
        'worksheet_views.js',
        'tree.js',
        'notifications.js',
        'globals.js',
        'keyshortcuts.js',
     )},
)
