// Function to hide flash messages after 10 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        var flashMessages = document.querySelectorAll('.flash_message');
        flashMessages.forEach(function(message) {
            message.messages.add('hide');
        });
    }, 10000);  // 10 seconds
});