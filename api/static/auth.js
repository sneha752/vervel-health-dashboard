document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const loginMessage = document.getElementById('login-message');
    const signupMessage = document.getElementById('signup-message');

    // Handle Login Form Submission (Simulated)
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            loginMessage.textContent = 'Login is disabled for this free deployment. Try entering any email and password to proceed (no actual authentication).';
            loginMessage.style.color = 'orange'; // Indicate it's a simulated login
            
            // Simulate a successful login after a short delay
            setTimeout(() => {
                // For Vercel, we can simply redirect. No session needs to be managed server-side persistently.
                window.location.href = '/'; 
            }, 1500);
        });
    }

    // Handle Signup Form Submission (Simulated)
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            signupMessage.textContent = 'Signup is disabled for this free deployment. Redirecting to login...';
            signupMessage.style.color = 'orange'; // Indicate it's a simulated signup
            setTimeout(() => {
                window.location.href = '/login'; 
            }, 2000);
        });
    }
});
