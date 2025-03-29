document.addEventListener('DOMContentLoaded', function() {
    const nameInput = document.getElementById('nameInput');
    const submitBtn = document.getElementById('submitBtn');
    const summarizeBtn = document.getElementById('summarizeBtn');
    const greetingDiv = document.getElementById('greeting');
    const summaryDiv = document.getElementById('summary');
    const loader = document.getElementById('loader');

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

    summarizeBtn.addEventListener('click', async function() {
        try {
            // Show loader
            loader.style.display = 'block';
            summaryDiv.style.display = 'none';

            // Get current tab URL
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            const url = tab.url;

            // Send request to backend
            const response = await fetch('http://localhost:5000/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Display summary
            summaryDiv.textContent = data.summary;
            summaryDiv.style.display = 'block';
        } catch (error) {
            summaryDiv.textContent = 'Error: ' + error.message;
            summaryDiv.style.display = 'block';
        } finally {
            // Hide loader
            loader.style.display = 'none';
        }
    });

    function updateGreeting(name) {
        greetingDiv.textContent = `Hello ${name}!`;
        greetingDiv.style.color = '#4CAF50';
    }
}); 