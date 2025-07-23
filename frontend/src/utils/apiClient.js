import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: API_URL
});

// Event for notifying about authentication errors
export const authEvents = {
  listeners: {},
  addListener: (event, callback) => {
    if (!authEvents.listeners[event]) {
      authEvents.listeners[event] = [];
    }
    authEvents.listeners[event].push(callback);
  },
  removeListener: (event, callback) => {
    if (authEvents.listeners[event]) {
      authEvents.listeners[event] = authEvents.listeners[event].filter(
        cb => cb !== callback
      );
    }
  },
  emit: (event, data) => {
    if (authEvents.listeners[event]) {
      authEvents.listeners[event].forEach(callback => callback(data));
    }
  }
};

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  config => {
    // Get token from localStorage
    const token = localStorage.getItem('authToken');
    
    // If token exists, add to headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor for handling auth errors
apiClient.interceptors.response.use(
  response => {
    return response;
  },
  async error => {
    const originalRequest = error.config;
    
    // If error is 401 (Unauthorized) and we haven't tried to refresh token yet
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      
      try {
        // Get current token
        const currentToken = localStorage.getItem('authToken');
        
        if (!currentToken) {
          // No token available, can't refresh
          throw new Error('No authentication token available');
        }
        
        // Try to refresh token
        const response = await axios.post(
          `${API_URL}/auth/refresh`,
          { token: currentToken }
        );
        
        const { token } = response.data;
        
        // Update token in localStorage
        localStorage.setItem('authToken', token);
        
        // Update Authorization header
        originalRequest.headers.Authorization = `Bearer ${token}`;
        
        // Retry original request
        return axios(originalRequest);
      } catch (refreshError) {
        // Token refresh failed
        console.error('Token refresh failed:', refreshError);
        
        // Clear token
        localStorage.removeItem('authToken');
        
        // Emit auth error event
        authEvents.emit('authError', { error: refreshError });
        
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Helper methods for common API operations
const api = {
  get: (url, config = {}) => apiClient.get(url, config),
  post: (data, url, config = {}) => apiClient.post(url, data, config),
  put: (data, url, config = {}) => apiClient.put(url, data, config),
  delete: (url, config = {}) => apiClient.delete(url, config),
  
  // Auth specific methods
  auth: {
    login: (googleToken) => apiClient.post('/auth/google', { token: googleToken }),
    logout: () => apiClient.post('/auth/logout'),
    getUser: () => apiClient.get('/auth/user'),
    refreshToken: (token) => apiClient.post('/auth/refresh', { token }),
    checkSession: () => apiClient.get('/auth/session')
  }
};

export default api;