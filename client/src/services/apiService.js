const API_BASE_URL = 'http://localhost:5000/api';

// Helper function to get auth header
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Helper function to handle response
const handleResponse = async (response) => {
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401) {
      // Handle unauthorized access (e.g., redirect to login)
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    const error = (data && data.error) || response.statusText;
    return Promise.reject(error);
  }
  return data;
};

export const authService = {
  // Authentication endpoints
  login: async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
      credentials: 'include',
    });
    const data = await handleResponse(response);
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
    }
    return data;
  },

  register: async (userData) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    return handleResponse(response);
  },

  getCurrentUser: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        ...getAuthHeader(),
      },
      credentials: 'include',
    });
    return handleResponse(response);
  },

  updateProfile: async (userId, userData) => {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(userData),
    });
    return handleResponse(response);
  },

  logout: () => {
    localStorage.removeItem('token');
  },
};

export const api = {
  // Car endpoints
  getCars: async () => {
    return api.get('/vehicles');
  },
  getCar: async (id) => {
    return api.get(`/vehicles/${id}`);
  },
  addCar: async (carData) => {
    return api.post('/vehicles', carData);
  },
  updateCar: async (id, carData) => {
    return api.put(`/vehicles/${id}`, carData);
  },
  deleteCar: async (id) => {
    return api.delete(`/vehicles/${id}`);
  },

  // Common HTTP methods
  get: async (endpoint) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        ...getAuthHeader(),
      },
      credentials: 'include',
    });
    return handleResponse(response);
  },

  post: async (endpoint, data) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
      credentials: 'include',
    });
    return handleResponse(response);
  },

  put: async (endpoint, data) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
      credentials: 'include',
    });
    return handleResponse(response);
  },

  delete: async (endpoint) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        ...getAuthHeader(),
      },
      credentials: 'include',
    });
    return handleResponse(response);
  }
};
