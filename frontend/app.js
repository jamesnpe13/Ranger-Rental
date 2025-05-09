document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://127.0.0.1:5000/api/items'; // Base API URL from your backend
    const carsContainer = document.getElementById('cars-container');
    const addCarForm = document.getElementById('add-car-form');
    const addCarFormSection = document.getElementById('add-car-form-section'); // Get the section
    const editCarFormSection = document.getElementById('edit-car-form-section');
    const editCarForm = document.getElementById('edit-car-form');
    const cancelEditButton = document.getElementById('cancel-edit');
    const userSessionInfo = document.getElementById('user-session-info');

    // Function to update user session display (login/logout status)
    function updateUserSessionDisplay() {
        console.log("[Debug] Updating user session display.");
        const username = localStorage.getItem('ranger_rental_username');
        const userRole = localStorage.getItem('ranger_rental_user_role');

        if (username && userRole) {
            userSessionInfo.innerHTML = `
                <span>Logged in as: <strong>${username}</strong> (${userRole})</span>
                <button id="logout-button" style="margin-left: 10px;">Logout</button>
            `;
            document.getElementById('logout-button').addEventListener('click', () => {
                localStorage.removeItem('ranger_rental_username');
                localStorage.removeItem('ranger_rental_user_role');
                console.log("[Debug] User logged out.");
                updateUserSessionDisplay(); // Update header
                fetchAndDisplayCars();    // Refresh car list (which will hide/show admin controls)
            });

            // Show/hide admin-specific sections
            if (userRole === 'admin') {
                if(addCarFormSection) addCarFormSection.style.display = 'block';
            } else {
                if(addCarFormSection) addCarFormSection.style.display = 'none';
            }
        } else {
            userSessionInfo.innerHTML = '
                <a href="login.html" style="text-decoration: none;"><button>Login</button></a>
            ';
            if(addCarFormSection) addCarFormSection.style.display = 'none'; // Hide add car form if not logged in
        }
    }

    // Function to fetch and display cars
    async function fetchAndDisplayCars() {
        console.log('[Debug] fetchAndDisplayCars: Started');
        try {
            const response = await fetch(apiUrl);
            console.log('[Debug] fetchAndDisplayCars: API response received', response.status);
            if (!response.ok) {
                console.error('[Debug] fetchAndDisplayCars: API response not OK', response);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const cars = await response.json();
            console.log('[Debug] fetchAndDisplayCars: Cars data received', cars);

            carsContainer.innerHTML = ''; // Clear loading message or previous cars
            console.log('[Debug] fetchAndDisplayCars: carsContainer cleared');

            if (cars.length === 0) {
                carsContainer.innerHTML = '<p>No cars available at the moment.</p>';
                console.log('[Debug] fetchAndDisplayCars: No cars available message shown');
                return;
            }

            cars.forEach(car => {
                const carItem = document.createElement('div');
                carItem.classList.add('car-item');
                carItem.dataset.id = car.id;

                const availableText = car.available ? 'Yes' : 'No';
                const availableClass = car.available ? 'available' : 'unavailable';

                carItem.innerHTML = `
                    <h3>${car.make} ${car.model} (${car.year})</h3>
                    <p class="price">Price per day: $${car.price_per_day.toFixed(2)}</p>
                    <p>Available: <span class="${availableClass}">${availableText}</span></p>
                    <button class="edit-btn" data-id="${car.id}">Edit</button>
                    <button class="delete-btn" data-id="${car.id}">Delete</button>
                `;
                carsContainer.appendChild(carItem);
            });
            console.log(`[Debug] fetchAndDisplayCars: ${cars.length} cars appended to container`);

            // Add event listeners using event delegation on the container
            carsContainer.addEventListener('click', (event) => {
                if (event.target.classList.contains('edit-btn')) {
                    const carId = event.target.dataset.id;
                    populateEditForm(carId);
                }
                if (event.target.classList.contains('delete-btn')) {
                    const carId = event.target.dataset.id;
                    handleDeleteCar(carId);
                }
            });

        } catch (error) {
            console.error('Error fetching cars:', error);
            carsContainer.innerHTML = '<p>Error loading cars. Please check the console.</p>';
        }
    }

    // Function to populate the edit form
    async function populateEditForm(carId) {
        try {
            const response = await fetch(`${apiUrl}/${carId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const car = await response.json();

            document.getElementById('edit-car-id').value = car.id;
            document.getElementById('edit-make').value = car.make;
            document.getElementById('edit-model').value = car.model;
            document.getElementById('edit-year').value = car.year;
            document.getElementById('edit-price').value = car.price_per_day;
            document.getElementById('edit-available').checked = car.available;

            editCarFormSection.style.display = 'block';
            editCarFormSection.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error('Error fetching car details for edit:', error);
            alert('Could not fetch car details for editing. Please check console.');
        }
    }

    // Initial fetch of cars
    fetchAndDisplayCars();

    // Add Car functionality
    addCarForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const make = document.getElementById('add-make').value;
        const model = document.getElementById('add-model').value;
        const year = parseInt(document.getElementById('add-year').value, 10);
        const price_per_day = parseFloat(document.getElementById('add-price').value);
        const available = document.getElementById('add-available').checked;

        const newCar = {
            make,
            model,
            year,
            price_per_day,
            available
        };

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newCar),
            });
            console.log('[Debug] Add Car: Response from POST', response.status, response.statusText);

            if (response.status === 201) {
                console.log('[Debug] Add Car: Success (201), resetting form and refreshing list.');
                addCarForm.reset(); // Clear the form
                fetchAndDisplayCars(); // Refresh the car list
                alert('Car added successfully!');
            } else {
                const errorData = await response.json();
                console.error('[Debug] Add Car: Error response', errorData);
                let errorMessage = `Error adding car (Status: ${response.status})`;
                if (errorData && errorData.message) {
                    errorMessage += `\nMessage: ${errorData.message}`;
                }
                if (errorData && errorData.errors) {
                    errorMessage += `\nDetails: ${JSON.stringify(errorData.errors)}`;
                }
                alert(errorMessage);
                console.error('Error adding car:', errorData);
            }
        } catch (error) {
            console.error('Network error or other issue adding car:', error);
            alert('Could not add car. Please check the console for more details.');
        }
    });

    // Edit Car functionality
    editCarForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const carId = document.getElementById('edit-car-id').value;

        const updatedCar = {
            make: document.getElementById('edit-make').value,
            model: document.getElementById('edit-model').value,
            year: parseInt(document.getElementById('edit-year').value, 10),
            price_per_day: parseFloat(document.getElementById('edit-price').value),
            available: document.getElementById('edit-available').checked
        };

        try {
            const response = await fetch(`${apiUrl}/${carId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedCar),
            });

            if (response.ok) {
                editCarFormSection.style.display = 'none'; // Hide the form
                editCarForm.reset();
                fetchAndDisplayCars(); // Refresh list
                alert('Car updated successfully!');
            } else {
                const errorData = await response.json();
                let errorMessage = `Error updating car (Status: ${response.status})`;
                if (errorData && errorData.message) errorMessage += `\nMessage: ${errorData.message}`;
                if (errorData && errorData.errors) errorMessage += `\nDetails: ${JSON.stringify(errorData.errors)}`;
                alert(errorMessage);
                console.error('Error updating car:', errorData);
            }
        } catch (error) {
            console.error('Network error or other issue updating car:', error);
            alert('Could not update car. Please check the console.');
        }
    });

    cancelEditButton.addEventListener('click', () => {
        editCarFormSection.style.display = 'none';
        editCarForm.reset();
    });

    // Function to handle car deletion
    async function handleDeleteCar(carId) {
        if (!confirm('Are you sure you want to delete this car?')) {
            return; // User cancelled the action
        }

        try {
            const response = await fetch(`${apiUrl}/${carId}`, {
                method: 'DELETE',
            });

            if (response.ok) { // Status 200-299, typically 200 or 204 for DELETE
                fetchAndDisplayCars(); // Refresh the car list
                alert('Car deleted successfully!');
            } else {
                const errorData = await response.json().catch(() => null); // Try to parse JSON, but don't fail if no body
                let errorMessage = `Error deleting car (Status: ${response.status})`;
                if (errorData && errorData.message) {
                    errorMessage += `\nMessage: ${errorData.message}`;
                }
                alert(errorMessage);
                console.error('Error deleting car:', errorData || response.statusText);
            }
        } catch (error) {
            console.error('Network error or other issue deleting car:', error);
            alert('Could not delete car. Please check the console for more details.');
        }
    }
});
