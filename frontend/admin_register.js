document.addEventListener('DOMContentLoaded', function() {
    const adminRegisterForm = document.getElementById('adminRegisterForm');
    const messageElement = document.getElementById('message');

    if (adminRegisterForm) {
        adminRegisterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            messageElement.textContent = ''; // Clear previous messages
            messageElement.className = 'message'; // Reset class

            const username = event.target.username.value;
            const password = event.target.password.value;
            const confirmPassword = event.target.confirmPassword.value;
            // const adminCode = event.target.adminCode ? event.target.adminCode.value : null; // If using an admin code

            if (!username || !password || !confirmPassword) {
                messageElement.textContent = 'All fields are required.';
                messageElement.classList.add('error-message');
                return;
            }

            if (password !== confirmPassword) {
                messageElement.textContent = 'Passwords do not match.';
                messageElement.classList.add('error-message');
                return;
            }

            // Optional: Add admin code validation here if implemented

            fetch('http://127.0.0.1:5001/api/admin/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    username: username, 
                    password: password 
                    // admin_code: adminCode // If using an admin code
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message === "Admin user registered successfully") {
                    messageElement.textContent = data.message + " You can now login.";
                    messageElement.classList.add('success-message'); // You might need to define .success-message style
                    adminRegisterForm.reset(); // Clear the form
                } else {
                    messageElement.textContent = data.message || 'Registration failed. Please try again.';
                    messageElement.classList.add('error-message');
                }
            })
            .catch(error => {
                console.error('Admin Registration Error:', error);
                messageElement.textContent = 'An error occurred during registration. Please try again.';
                messageElement.classList.add('error-message');
            });
        });
    }
});

// Add to your admin_style.css or style.css:
/*
.success-message {
    color: green;
    text-align: center;
    margin-top: 10px;
}
.error-message {
    color: red;
    text-align: center;
    margin-top: 10px;
}
*/
