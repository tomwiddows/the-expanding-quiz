// Function to hide flash messages after 10 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        // Select all elements with the class 'flash_message'
        var flashMessages = document.querySelectorAll('.flash_message');
        // Iterate over each flash message
        flashMessages.forEach(function(message) {
            // Add the 'hide' class to each message
            // Note: There's a typo here. It should be message.classList.add('hide');
            message.messages.add('hide');
        });
    }, 10000);  // Wait for 10 seconds (10000 milliseconds) before executing
});

// Function to initialize and handle modal dialogs
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modal elements
    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems);
    
    // Add click event listeners to all modal trigger buttons
    var editButtons = document.querySelectorAll('.modal-trigger');
    editButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            // Prevent the default action of the button (e.g., following a link)
            e.preventDefault();
            // Get the ID of the modal associated with this button
            var modalId = this.getAttribute('href');
            // Get the Modal instance for this ID
            var modalInstance = M.Modal.getInstance(document.querySelector(modalId));
            // Open the modal
            modalInstance.open();
        });
    });
});