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
        'css/blackbird.css',
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

    # Base Javascript libraries
    {"type": "javascript",
     "name": "base_js",
     "path": MEDIA_ROOT + "js/vendor/",
     "url": MEDIA_URL + "js/vendor/",
     "minify": False,
     "files": (
        # External libraries
        #'head.js',
        'brequire.js',
        'blackbird.js',

        'json2.js',
        'jquery-mathml.js',
        'jquery-ui.js',
        'socket.io.js',

        'underscore.js',
        'backbone.js',
        'layout.js',

        'async.js',
        'pnotify.js',
        'keys.js',
        'hoverintent.js',
        #'sanitize.js',
        'rte.js',
        'editable.js',
        'autocomplete.js',
        'pattern_match.js',
     )},

    {"type": "javascript",
     "name": "unittest_js",
     "path": MEDIA_ROOT + "js/test/",
     "url": MEDIA_URL + "js/tests/",
     "minify": False,
     "files": (
        # External libraries
        #'head.js',
        'qunit.js',
        #'jquery.mockjax.min.js',
        'jslitmus.js',
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
#        'editable.js',
        'tree.js',
        'worksheet_managers.js',
        'worksheet_views.js',
        'worksheet_models.js',
        'notifications.js',
        'globals.js',
        'keyshortcuts.js',

         # Generated coffeescript
        'init.js',
        'utils.js',
        'base.js',
        'messages.js',
        'connection.js',
        'tasks.js'
     )},
)
