// This script handles the login and signup form submissions
// and communicates with the backend for authentication.

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const loginMessage = document.getElementById('login-message');
    const signupMessage = document.getElementById('signup-message');

    // Handle Login Form Submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            loginMessage.textContent = ''; // Clear previous messages

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();
                if (response.ok) {
                    // Redirect to the main dashboard on successful login
                    window.location.href = '/';
                } else {
                    loginMessage.textContent = data.error || 'Login failed. Please check your credentials.';
                }
            } catch (error) {
                console.error('Error during login:', error);
                loginMessage.textContent = 'An error occurred. Please try again.';
            }
        });
    }

    // Handle Signup Form Submission
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;

            signupMessage.textContent = ''; // Clear previous messages

            try {
                const response = await fetch('/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();
                if (response.ok) {
                    signupMessage.textContent = 'Account created successfully! Redirecting to login...';
                    signupMessage.style.color = 'green';
                    setTimeout(() => {
                        window.location.href = '/login'; // Redirect to login after successful signup
                    }, 2000);
                } else {
                    signupMessage.textContent = data.error || 'Signup failed. Please try again.';
                }
            } catch (error) {
                console.error('Error during signup:', error);
                signupMessage.textContent = 'An error occurred. Please try again.';
            }
        });
    }
});
