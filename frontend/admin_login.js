document.addEventListener('DOMContentLoaded', function() {
    const adminLoginForm = document.getElementById('adminLoginForm');
    const errorMessage = document.getElementById('errorMessage');

    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission
            errorMessage.textContent = ''; // Clear any previous error messages

            const formData = new FormData(adminLoginForm);
            const email = formData.get('email');
            const password = formData.get('password');

            console.log('Admin Login Attempt:', { email });

            // Basic client-side validation
            if (!email || !password) {
                errorMessage.textContent = 'Email and password are required.';
                return;
            }

            try {
                const response = await fetch('/admin/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({ email, password }).toString(),
                    redirect: 'manual', // Handle redirects manually
                    credentials: 'same-origin'  // Important for session cookies
                });

                if (response.ok || response.redirected) {
                    // If we got redirected, it means login was successful
                    window.location.href = response.url || '/admin/dashboard';
                } else {
                    const data = await response.json().catch(() => ({}));
                    throw new Error(data.error || `Login failed (${response.status}). Please try again.`);
                }
            } catch (error) {
                console.error('Admin Login Error:', error);
                errorMessage.textContent = error.message || 'An error occurred during login. Please try again.';
            }
        });
    }
});
