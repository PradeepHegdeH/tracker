document.addEventListener('DOMContentLoaded', function() {
    const nameInput = document.getElementById('nameInput');
    const submitBtn = document.getElementById('submitBtn');
    const greetingDiv = document.getElementById('greeting');

    // Load saved name if it exists
    chrome.storage.local.get(['userName'], function(result) {
        if (result.userName) {
            nameInput.value = result.userName;
            updateGreeting(result.userName);
        }
    });

    submitBtn.addEventListener('click', function() {
        const name = nameInput.value.trim();
        if (name) {
            // Save the name
            chrome.storage.local.set({ userName: name }, function() {
                updateGreeting(name);
            });
        }
    });

    function updateGreeting(name) {
        greetingDiv.textContent = `Hello ${name}!`;
        greetingDiv.style.color = '#4CAF50';
    }
}); 