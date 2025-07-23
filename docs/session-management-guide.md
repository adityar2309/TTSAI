# Session Management Guide

This guide explains the session management implementation for the application.

## Overview

The session management system handles:

1. Authentication token storage and retrieval
2. Automatic token refresh
3. Session timeout warnings
4. Session expiration handling

## Components

### Session Service

The `sessionService` provides core functionality for managing authentication sessions:

- Token storage and retrieval
- Automatic token refresh
- Session verification
- Session timeout detection

### API Client

The `apiClient` handles authenticated API requests:

- Automatically adds authentication tokens to requests
- Handles 401 errors with token refresh
- Emits authentication events for global handling

### Session Timeout Warning

The `SessionTimeoutWarning` component displays a warning when the session is about to expire:

- Shows a countdown timer
- Allows the user to continue the session
- Provides an option to log out

## Integration

### App Component

Add the `SessionTimeoutWarning` component to your App component:

```jsx
// src/App.js
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import GoogleOAuthProvider from './components/auth/GoogleOAuthProvider';
import SessionTimeoutWarning from './components/auth/SessionTimeoutWarning';
// ... other imports

function App() {
  return (
    <GoogleOAuthProvider>
      <Router>
        {/* Your routes and components */}
        <SessionTimeoutWarning />
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
```

### Using the API Client

Use the API client for all API requests to ensure proper authentication:

```jsx
import api from '../utils/apiClient';

// Example component
const MyComponent = () => {
  const fetchData = async () => {
    try {
      // API client automatically adds authentication headers
      const response = await api.get('/some-endpoint');
      return response.data;
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  
  // ...
};
```

## Configuration

The session management system has several configurable parameters in `sessionService.js`:

- `REFRESH_INTERVAL`: How often to refresh the token (default: 15 minutes)
- `WARNING_BEFORE_TIMEOUT`: How long before expiry to show warning (default: 5 minutes)
- `TOKEN_KEY`: Storage key for the authentication token (default: 'authToken')

## Security Considerations

1. **Token Storage**: Tokens are stored in localStorage, which is vulnerable to XSS attacks. In a production environment, consider using HTTP-only cookies for token storage.

2. **Token Refresh**: The system automatically refreshes tokens before they expire. Ensure your backend properly validates refresh requests.

3. **Session Timeout**: Users are warned before their session expires and given the option to continue or log out.

4. **HTTPS**: Always use HTTPS in production to protect token transmission.

## Troubleshooting

### Common Issues

1. **"Session expired" errors**
   - Check that the token refresh is working correctly
   - Verify that the backend is accepting refresh requests
   - Check that the token expiration time is set correctly

2. **Multiple refresh requests**
   - Check for duplicate initialization of the session service
   - Ensure timers are properly cleared when components unmount

3. **Session warning not showing**
   - Verify that the token contains an expiration claim
   - Check that the warning time is set correctly
   - Ensure the SessionTimeoutWarning component is mounted

### Debugging

1. Enable debug logging in sessionService:

```javascript
// Add to sessionService.js
const DEBUG = true;

function debugLog(...args) {
  if (DEBUG) {
    console.log('[SessionService]', ...args);
  }
}

// Then use debugLog instead of console.log
```

2. Monitor token refresh requests in the browser's network tab

3. Check localStorage to verify token updates