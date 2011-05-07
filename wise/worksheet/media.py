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

    {"type": "css",
     "name": "ecosystem_css",
     "path": MEDIA_ROOT,
     "url": MEDIA_URL,
     "minify": False,
     "files": (
        'css/ecosystem.css',
     )},

    # Worksheet stylesheets
    {"type": "css",
     "name": "worksheet_css",
     "path": MEDIA_ROOT + "css/",
     "url": MEDIA_URL + "css/",
     "minify": False,
     "files": (
        'fonts.css',
        'math.css',
        'mathml.css',
        'worksheet.css',
        'autocomplete.css',
        'superfish.css',
     )},

    # Base Javascript libraries, mostly jQuery plugins, backbone
    # and underscore
    {"type": "javascript",
     "name": "base_js",
     "path": MEDIA_ROOT + "js/",
     "url": MEDIA_URL + "js/",
     "minify": False,
     "files": (
        # External libraries
        'head.js',
        'brequire.js',

        'jquery.js',
        'jquery-ui.js',
        'layout.js',
        'json2.js',
        'underscore.js',
        'backbone.js',
        'async.js',
        'pnotify.js',
        'keys.js',
        'hoverintent.js',
        #'sanitize.js',
        'rte.js',
        'editable.js',
     )},

    {"type": "javascript",
     "name": "worksheet_js",
     "path": MEDIA_ROOT + "js/",
     "url": MEDIA_URL + "js/",
     "minify": False,
     "files": (
        'worksheet_init.js',
        'worksheet.js',
        'interactions.js',
        'worksheet_ui.js',
#        'editable.js',
        'tree.js',
        'worksheet_managers.js',
        'worksheet_views.js',
        'worksheet_models.js',
        'notifications.js',
        'pattern_match.js',
        'globals.js',
        'keyshortcuts.js',
        'autocomplete.js',

         # Generated coffeescript
        'utils.js',
        'socket.io.js',
        'base.js',
        'messages.js',
        'connection.js',
        'tasks.js'
     )},
)
