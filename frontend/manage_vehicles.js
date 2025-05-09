document.addEventListener('DOMContentLoaded', function() {
    const addVehicleForm = document.getElementById('add-vehicle-form');
    const messageElement = document.getElementById('message');
    const existingVehiclesListElement = document.getElementById('existing-vehicles-list');
    const editVehicleSection = document.getElementById('edit-vehicle-section');
    const editVehicleForm = document.getElementById('edit-vehicle-form');
    const editMessageElement = document.getElementById('edit-message');
    const cancelEditButton = document.getElementById('cancel-edit-button');

    function fetchAndRenderVehicles() {
        fetch('http://127.0.0.1:5001/api/items') // Assuming /api/items GET returns all cars
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.statusText);
                }
                return response.json();
            })
            .then(vehicles => {
                existingVehiclesListElement.innerHTML = ''; // Clear existing list
                if (vehicles.length === 0) {
                    existingVehiclesListElement.innerHTML = '<p>No vehicles found.</p>';
                    return;
                }

                const ul = document.createElement('ul');
                vehicles.forEach(vehicle => {
                    const li = document.createElement('li');
                    li.textContent = `${vehicle.year} ${vehicle.make} ${vehicle.model} - $${vehicle.price_per_day}/day - ${vehicle.available ? 'Available' : 'Not Available'}`;
                    
                    const editButton = document.createElement('button');
                    editButton.textContent = 'Edit';
                    editButton.classList.add('edit-button'); // For styling
                    editButton.dataset.vehicleId = vehicle.id;
                    editButton.addEventListener('click', function() {
                        // The 'vehicle' object from the loop is directly available here due to closure
                        populateEditForm(vehicle);
                    });

                    li.appendChild(editButton);
                    // TODO: Add delete buttons here later
                    ul.appendChild(li);
                });
                existingVehiclesListElement.appendChild(ul);
            })
            .catch(error => {
                console.error('Error fetching vehicles:', error);
                existingVehiclesListElement.innerHTML = '<p class="error-message">Error loading vehicles. Please try again.</p>';
            });
    }

    if (addVehicleForm) {
        addVehicleForm.addEventListener('submit', function(event) {
            event.preventDefault();
            messageElement.textContent = ''; // Clear previous messages
            messageElement.className = 'message'; // Reset class

            const make = event.target.make.value;
            const model = event.target.model.value;
            const year = parseInt(event.target.year.value);
            const price_per_day = parseFloat(event.target.price_per_day.value);
            const available = event.target.available.checked;

            if (!make || !model || !year || !price_per_day) {
                messageElement.textContent = 'Make, Model, Year, and Price are required.';
                messageElement.className = 'error-message';
                return;
            }

            const vehicleData = {
                make: make,
                model: model,
                year: year,
                price_per_day: price_per_day,
                available: available
            };

            // TODO: Replace with actual API endpoint
            fetch('http://127.0.0.1:5001/api/admin/vehicles', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // TODO: Add Authorization header if admin authentication is implemented
                    // 'Authorization': 'Bearer ' + adminAuthToken 
                },
                body: JSON.stringify(vehicleData)
            })
            .then(response => {
                if (!response.ok) {
                    // Try to get error message from backend, otherwise use default
                    return response.json().then(err => { throw err; }).catch(() => { throw new Error('Server responded with status ' + response.status); });
                }
                return response.json();
            })
            .then(data => {
                messageElement.textContent = data.message || 'Vehicle added successfully!';
                messageElement.className = 'success-message';
                addVehicleForm.reset();
                fetchAndRenderVehicles(); // Refresh the list
            })
            .catch(error => {
                console.error('Error adding vehicle:', error);
                if (error.message) {
                    messageElement.textContent = 'Error: ' + error.message;
                } else if (error.errors && Array.isArray(error.errors) && error.errors.length > 0) {
                    // If backend returns validation errors
                    messageElement.textContent = 'Error: ' + error.errors.map(e => e.msg).join(', ');
                }
                else {
                    messageElement.textContent = 'An error occurred while adding the vehicle. Please try again.';
                }
                messageElement.className = 'error-message';
            });
        });
    }

    function populateEditForm(vehicle) {
        if (!editVehicleForm || !editVehicleSection) return;

        editVehicleForm.elements['edit-vehicle-id'].value = vehicle.id;
        editVehicleForm.elements['edit-make'].value = vehicle.make;
        editVehicleForm.elements['edit-model'].value = vehicle.model;
        editVehicleForm.elements['edit-year'].value = vehicle.year;
        editVehicleForm.elements['edit-price_per_day'].value = vehicle.price_per_day;
        editVehicleForm.elements['edit-available'].checked = vehicle.available; // Assuming backend returns boolean
        
        editMessageElement.textContent = '';
        editMessageElement.className = 'message';
        editVehicleSection.style.display = 'block';
        addVehicleForm.style.display = 'none'; // Optionally hide add form
    }

    if (cancelEditButton) {
        cancelEditButton.addEventListener('click', function() {
            editVehicleSection.style.display = 'none';
            editMessageElement.textContent = '';
            addVehicleForm.style.display = 'block'; // Show add form again
        });
    }

    if (editVehicleForm) {
        editVehicleForm.addEventListener('submit', function(event) {
            event.preventDefault();
            editMessageElement.textContent = '';
            editMessageElement.className = 'message';

            const vehicleId = event.target.elements['edit-vehicle-id'].value;
            const make = event.target.elements['edit-make'].value;
            const model = event.target.elements['edit-model'].value;
            const year = parseInt(event.target.elements['edit-year'].value);
            const price_per_day = parseFloat(event.target.elements['edit-price_per_day'].value);
            const available = event.target.elements['edit-available'].checked;

            if (!make || !model || !year || !price_per_day) {
                editMessageElement.textContent = 'Make, Model, Year, and Price are required.';
                editMessageElement.className = 'error-message';
                return;
            }

            const updatedVehicleData = {
                make: make,
                model: model,
                year: year,
                price_per_day: price_per_day,
                available: available
            };

            fetch(`http://127.0.0.1:5001/api/items/${vehicleId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    // TODO: Add Authorization header if needed
                },
                body: JSON.stringify(updatedVehicleData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; }).catch(() => { throw new Error('Server responded with status ' + response.status); });
                }
                return response.json();
            })
            .then(data => {
                editMessageElement.textContent = data.message || 'Vehicle updated successfully!'; // Backend might not send a message for PUT
                editMessageElement.className = 'success-message';
                fetchAndRenderVehicles(); // Refresh the list
                setTimeout(() => { // Give user time to see success message
                    editVehicleSection.style.display = 'none';
                    addVehicleForm.style.display = 'block';
                }, 1500);
            })
            .catch(error => {
                console.error('Error updating vehicle:', error);
                let errorMessage = 'An error occurred while updating the vehicle. Please try again.';
                if (error.message) {
                    errorMessage = 'Error: ' + error.message;
                }
                if (error.errors) { // Backend validation errors
                    const fieldErrors = Object.entries(error.errors).map(([field, msg]) => `${field}: ${msg}`).join(', ');
                    errorMessage = `Validation failed: ${fieldErrors}`;
                }
                editMessageElement.textContent = errorMessage;
                editMessageElement.className = 'error-message';
            });
        });
    }

    // Initial load of vehicles
    if (existingVehiclesListElement) {
        fetchAndRenderVehicles();
    }
});
