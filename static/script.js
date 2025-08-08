// Get DOM elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatWindow = document.getElementById('chat-window');
const reportUpload = document.getElementById('report-upload');
const reportSummary = document.getElementById('report-summary');
const dietPlanList = document.getElementById('diet-plan');
const habitsList = document.getElementById('habits-list');
const healthRisk = document.getElementById('health-risk');
const healthChart = document.getElementById('health-chart');
const logoutButton = document.getElementById('logout-button');
const userIdDisplay = document.getElementById('user-id-display');

// Smartwatch elements
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

// Handle health report file upload
reportUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData(); 
    formData.append('file', file); 
    reportSummary.textContent = 'Analyzing report, please wait...';
    dietPlanList.innerHTML = '';
    habitsList.innerHTML = '';
    healthChart.classList.add('hidden'); // Hide chart while loading
    
    try {
        const response = await fetch('/upload-report', {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (response.ok) {
            reportSummary.textContent = data.summary;
            healthRisk.textContent = `Health Risk: ${data.health_risk.toUpperCase()}`;
            
            data.diet_plan.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                dietPlanList.appendChild(li);
            });
            
            data.habits.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                habitsList.appendChild(li);
            });

            if (data.chart_url) {
                healthChart.src = data.chart_url;
                healthChart.classList.remove('hidden');
            }
        } else {
            reportSummary.textContent = `Error: ${data.error}`;
            healthRisk.textContent = '';
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        reportSummary.textContent = 'Error uploading report. Please try again.';
        healthRisk.textContent = '';
    }
});

// Handle smartwatch data upload
smartwatchUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    smartwatchUploadMessage.textContent = 'Uploading and processing smartwatch data...';
    smartwatchSummary.textContent = 'Loading smartwatch data summary...';

    const formData = new FormData(); 
    formData.append('file', file); 

    try {
        const response = await fetch('/upload-smartwatch-data', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();
        if (response.ok) {
            smartwatchUploadMessage.textContent = data.message;
            if (data.summary) {
                let summaryText = '';
                if (data.summary.type === 'activity_data') {
                    summaryText = `
                        <strong>Activity Data Summary:</strong><br>
                        Average Daily Steps: ${data.summary.average_daily_steps.toFixed(0)}<br>
                        Average Daily Calories: ${data.summary.average_daily_calories.toFixed(0)}<br>
                        Total Very Active Minutes: ${data.summary.total_very_active_minutes}<br>
                        Total Sedentary Minutes: ${data.summary.total_sedentary_minutes}
                    `;
                } else if (data.summary.type === 'generic_smartwatch_data') {
                    summaryText = `
                        <strong>Generic Smartwatch Data Summary:</strong><br>
                        Average Heart Rate: ${data.summary.average_heart_rate.toFixed(1)} bpm<br>
                        Total Steps: ${data.summary.total_steps}
                    `;
                }
                smartwatchSummary.innerHTML = summaryText; // Use innerHTML for formatted text
            }
        } else {
            smartwatchUploadMessage.textContent = `Error: ${data.error}`;
            smartwatchSummary.textContent = 'Failed to load smartwatch data.';
        }
    } catch (error) {
        console.error('Error uploading smartwatch data:', error);
        smartwatchUploadMessage.textContent = 'Error uploading smartwatch data. Please try again.';
        smartwatchSummary.textContent = 'Failed to load smartwatch data.';
    }
});


// Handle Logout
if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/logout', { method: 'POST' });
            if (response.ok) {
                window.location.href = '/login'; // Redirect to login page after logout
            } else {
                console.error('Logout failed.');
            }
        } catch (error) {
            console.error('Error during logout:', error);
        }
    });
}

// Fetch user ID on page load for the dashboard
document.addEventListener('DOMContentLoaded', async () => {
    if (userIdDisplay) {
        try {
            const response = await fetch('/get-user-id');
            const data = await response.json();
            if (response.ok && data.userId) {
                userIdDisplay.textContent = `User ID: ${data.userId}`;
            } else {
                userIdDisplay.textContent = 'User ID: Not logged in';
                if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
                    window.location.href = '/login';
                }
            }
        } catch (error) {
            console.error('Error fetching user ID:', error);
            userIdDisplay.textContent = 'User ID: Error';
            if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
                window.location.href = '/login';
            }
        }
    }
});
