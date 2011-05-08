///////////////////////////////////////////////////////////
// Notifications
///////////////////////////////////////////////////////////

var notify = {
    info: 
        function(text) { 
            $.pnotify({
                ''            : 'Regular Notice',
                pnotify_text  : text,
                pnotify_delay : 5000
            });
        },
        
    error: 
        function(text) {
            $.pnotify({
                'Error'       : 'Regular Notice',
                pnotify_text  : text,
                pnotify_delay : 5000,
                pnotify_type : 'error'
            });
        }
};

// Consume the alert function and wrap out into a notification
// For compatability reasons
window.alert = notify.info;
window.error = notify.error;
