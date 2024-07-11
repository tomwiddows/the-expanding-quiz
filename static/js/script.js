// Function to hide flash messages after 10 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        var flashMessages = document.querySelectorAll('.flash_message');
        flashMessages.forEach(function(message) {
            message.messages.add('hide');
        });
    }, 10000);  // 10 seconds
});

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems);
    
    var editButtons = document.querySelectorAll('.modal-trigger');
    editButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var modalId = this.getAttribute('href');
            var modalInstance = M.Modal.getInstance(document.querySelector(modalId));
            modalInstance.open();
        });
    });
});
  