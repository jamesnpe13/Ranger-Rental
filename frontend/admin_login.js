document.addEventListener('DOMContentLoaded', function() {
    const adminLoginForm = document.getElementById('adminLoginForm');
    const errorMessage = document.getElementById('errorMessage');

    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission
            errorMessage.textContent = ''; // Clear any previous error messages

            const username = event.target.username.value;
            const password = event.target.password.value;

            console.log('Admin Login Attempt:', { username, password });

            // Basic client-side validation (can be expanded)
            if (!username || !password) {
                errorMessage.textContent = 'Username and password are required.';
                return;
            }

            // Send credentials to the backend for verification
            fetch('http://127.0.0.1:5001/api/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === "Admin login successful") {
                    // Store user info if needed, e.g., in localStorage
                    // localStorage.setItem('adminUser', JSON.stringify({ username: data.username, role: data.role }));
                    window.location.href = 'admin_panel.html'; // Redirect to admin panel
                } else {
                    errorMessage.textContent = data.message || 'Login failed. Please try again.';
                }
            })
            .catch(error => {
                console.error('Admin Login Error:', error);
                errorMessage.textContent = 'An error occurred during login. Please try again.';
            });
        });
    }
});
