// Get DOM elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatWindow = document.getElementById('chat-window');
const reportUpload = document.getElementById('report-upload'); // Still exists but disabled
const reportSummary = document.getElementById('report-summary');
const dietPlanList = document.getElementById('diet-plan');
const habitsList = document.getElementById('habits-list');
const healthRisk = document.getElementById('health-risk');
const healthChart = document.getElementById('health-chart');
const logoutButton = document.getElementById('logout-button');
const userIdDisplay = document.getElementById('user-id-display');

// Smartwatch elements (still exist but disabled)
const smartwatchUpload = document.getElementById('smartwatch-upload');
const smartwatchUploadMessage = document.getElementById('smartwatch-upload-message');
const smartwatchSummary = document.getElementById('smartwatch-summary');


// Function to add a message to the chat window
function addMessage(sender, message) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('flex', 'items-start', 'space-x-2', 'mb-4');
    const messageSpan = document.createElement('span');
    messageSpan.classList.add('p-3', 'rounded-xl', 'max-w-xs', 'break-words');
    if (sender === 'user') {
        messageContainer.classList.add('justify-end');
        messageSpan.classList.add('bg-blue-500', 'text-white', 'rounded-br-none');
    } else {
        messageSpan.classList.add('bg-gray-200', 'text-gray-800', 'rounded-bl-none');
    }
    
    // Convert markdown (like **bold**) to HTML for display
    let formattedMessage = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedMessage = formattedMessage.replace(/\n/g, '<br>'); // Preserve newlines

    messageSpan.innerHTML = formattedMessage; // Use innerHTML for formatted text
    messageContainer.appendChild(messageSpan);
    chatWindow.appendChild(messageContainer);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Handle chat form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault(); 
    const message = userInput.value.trim();
    if (!message) return;
    addMessage('user', message);
    userInput.value = '';
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });
        const data = await response.json();
        addMessage('bot', data.response);
    } catch (error) {
        console.error('Error:', error);
        addMessage('bot', 'Sorry, I am unable to connect right now. Please try again later.');
    }
});

// Handle report file upload (Will just show a disabled message)
reportUpload.addEventListener('change', async (e) => {
    reportSummary.textContent = 'Health report analysis is disabled in this deployment.';
    healthRisk.textContent = '';
    dietPlanList.innerHTML = '<li>Feature disabled in this deployment.</li>';
    habitsList.innerHTML = '<li>Feature disabled in this deployment.</li>';
    healthChart.classList.add('hidden');
});

// Handle smartwatch data upload (Will just show a disabled message)
smartwatchUpload.addEventListener('change', async (e) => {
    smartwatchUploadMessage.textContent = 'Smartwatch data analysis is disabled in this deployment.';
    smartwatchSummary.textContent = 'Smartwatch data analysis is disabled.';
});


// Handle Logout (Simulated)
if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
        // Clear local storage or session if used for client-side persistence (optional)
        // localStorage.removeItem('user_id'); 
        console.log("Simulating logout. No persistent server-side session.");
        window.location.href = '/login'; // Redirect to login page after logout
    });
}

// Check login status on page load (Simulated)
document.addEventListener('DOMContentLoaded', async () => {
    // For Vercel free tier, there's no persistent server-side user ID.
    // The dashboard will always be accessible if direct navigation is allowed,
    // or you can implement a simple client-side check if a 'login' was simulated.
    userIdDisplay.textContent = 'User ID: Not Persistent (Login simulated)';
    // If you always want to force users through the login page (even if simulated),
    // you can uncomment this:
    // if (window.location.pathname === '/' && !localStorage.getItem('simulated_login')) {
    //     window.location.href = '/login';
    // }
});
