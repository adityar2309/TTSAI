# Frontend Authentication Integration Guide

This guide explains how to integrate the Google OAuth authentication components into the frontend application.

## Prerequisites

1. Google OAuth client ID (see `docs/google-oauth-setup.md`)
2. Updated environment variables in `.env` files
3. Installed required dependencies (see `docs/frontend-dependencies.md`)

## Integration Steps

### 1. Update App.js

Wrap your application with the `GoogleOAuthProvider` component:

```jsx
// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GoogleOAuthProvider from './components/auth/GoogleOAuthProvider';
import LoginPage from './pages/LoginPage';
import LearningToolsPage from './pages/LearningToolsPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
// ... other imports

function App() {
  return (
    <GoogleOAuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route 
            path="/learning-tools" 
            element={
              <ProtectedRoute>
                <LearningToolsPage />
              </ProtectedRoute>
            } 
          />
          {/* ... other routes */}
        </Routes>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
```

### 2. Add Login Button to Header

Add the Google Sign-In button to your header or navigation component:

```jsx
// src/components/Header.js
import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import GoogleSignInButton from './auth/GoogleSignInButton';
import UserProfile from './auth/UserProfile';

const Header = () => {
  const { isAuthenticated } = useAuth();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Speech Translator
        </Typography>
        
        <Box>
          {isAuthenticated ? (
            <UserProfile />
          ) : (
            <GoogleSignInButton />
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
```

### 3. Use Authentication in Components

Use the `useAuth` hook to access authentication state and functions in your components:

```jsx
// Example component
import React from 'react';
import { Button } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const ProfileButton = () => {
  const { isAuthenticated, user, logout } = useAuth();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div>
      <p>Welcome, {user.name}!</p>
      <Button onClick={logout}>Logout</Button>
    </div>
  );
};

export default ProfileButton;
```

### 4. Protect Routes

Use the `ProtectedRoute` component to protect routes that require authentication:

```jsx
// In your route definitions
<Route 
  path="/protected-page" 
  element={
    <ProtectedRoute redirectTo="/login">
      <ProtectedPage />
    </ProtectedRoute>
  } 
/>
```

### 5. Add Authentication to API Calls

Create an authenticated API client:

```jsx
// src/utils/apiClient.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const apiClient = axios.create({
  baseURL: API_URL
});

// Add authentication interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't tried to refresh token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh token
        const token = localStorage.getItem('authToken');
        const refreshResponse = await axios.post(`${API_URL}/auth/refresh`, { token });
        
        // Update token in storage
        localStorage.setItem('authToken', refreshResponse.data.token);
        
        // Update header and retry request
        originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.token}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // If refresh fails, redirect to login
        localStorage.removeItem('authToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

## Testing Authentication

1. Start the frontend development server:
```bash
cd frontend
npm start
```

2. Navigate to the login page and test the Google Sign-In button.

3. After successful login, verify that:
   - User profile is displayed
   - Protected routes are accessible
   - API calls include the authentication token

## Troubleshooting

### Common Issues

1. **"Error: Google OAuth client ID is not configured"**
   - Check that `REACT_APP_GOOGLE_CLIENT_ID` is set in your `.env` file
   - Verify that the client ID is correct

2. **"Login failed" error**
   - Check browser console for detailed error messages
   - Verify that the backend authentication service is running
   - Check that the API URL is correct in `.env`

3. **"Invalid token" error**
   - The token may have expired - try logging out and back in
   - Check that the JWT secret is the same in frontend and backend

4. **CORS errors**
   - Ensure that the backend CORS configuration allows requests from the frontend origin

### Debugging Tips

1. Check browser console for errors
2. Use browser developer tools to inspect network requests
3. Check localStorage to verify token storage
4. Use the React Developer Tools extension to inspect component state