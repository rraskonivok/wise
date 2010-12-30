var Notifications = {
  AJAX_FAIL: {
    message: 'Worker did not respond to request.',
    type: 'error'
  },
  
  RULE_FAILED: {
    message: 'Failed to apply rule.',
    type: 'error'
  },
  
  COMMIT_SUCCESS: {
    message: 'Changes saved.',
    type: 'notice',
    icon: 'ui-icon ui-icon-disk',
  },

  COMMIT_FAIL: {
    message: 'Could not save.',
    type: 'error',
  },

  raise: function(handle) {
    var message = this[handle];

    $.pnotify({
        pnotify_title: message.title,
        pnotify_text: message.message,
        pnotify_type: message.type,
        pnotify_nonblock: true,
        pnotify_notice_icon: message.icon,
    });
  }
};

function alert(handle) {
    Notifications.raise(handle);
}
