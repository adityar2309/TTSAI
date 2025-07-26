# Authentication System Documentation

This directory contains a comprehensive authentication system for the Learning Tools application, implementing Google OAuth authentication with JWT token management.

## Components Overview

### Core Components

#### `AuthProvider.js`
Main authentication provider that wraps the entire application with Google OAuth and authentication context.

**Features:**
- Google OAuth initialization
- Global error handling
- Loading states
- Configuration validation

**Usage:**
```jsx
import { AuthProvider } from './components/auth';

function App() {
  return (
    <AuthProvider>
      <YourApp />
    </AuthProvider>
  );
}
```

#### `GoogleSignInButton.js`
Customizable Google sign-in button component with various styling options.

**Props:**
- `onSuccess`: Callback for successful authentication
- `onError`: Callback for authentication errors
- `variant`: Button variant ('contained', 'outlined')
- `size`: Button size ('small', 'medium', 'large')
- `fullWidth`: Whether button should take full width
- `text`: Custom button text

**Usage:**
```jsx
<GoogleSignInButton
  fullWidth
  variant="contained"
  onSuccess={(user) => console.log('Signed in:', user)}
  onError={(error) => console.error('Error:', error)}
/>
```

#### `UserProfile.js`
Flexible user profile component with multiple display variants.

**Variants:**
- `menu`: Dropdown menu with user info and actions
- `card`: Card layout with detailed user information
- `minimal`: Compact display with avatar and name

**Usage:**
```jsx
<UserProfile 
  variant="menu"
  showLastLogin={true}
  onSettingsClick={() => navigate('/settings')}
  onProfileClick={() => navigate('/profile')}
/>
```

### Utility Components

#### `AuthGuard.js`
Component that conditionally renders content based on authentication status.

**Usage:**
```jsx
<AuthGuard requireAuth={true}>
  <ProtectedContent />
</AuthGuard>
```

#### `AuthStatus.js`
Displays current authentication status with various detail levels.

**Variants:**
- `minimal`: Simple status chip
- `compact`: Status with user info and actions
- `detailed`: Full status card with session information

#### `AuthWrapper.js`
Higher-order component for wrapping components that require authentication.

#### `ProtectedRoute.js`
Route wrapper that redirects unauthenticated users to login.

**Usage:**
```jsx
<ProtectedRoute redirectTo="/login">
  <PrivatePage />
</ProtectedRoute>
```

#### `SessionTimeoutWarning.js`
Modal dialog that warns users about session expiration and allows session extension.

### Hooks

#### `useAuth`
Main authentication hook providing access to authentication state and methods.

**Returns:**
- `user`: Current user object
- `token`: JWT token
- `isAuthenticated`: Authentication status
- `isLoading`: Loading state
- `error`: Current error message
- `login(googleToken)`: Login method
- `logout()`: Logout method
- `refreshToken()`: Token refresh method
- `clearError()`: Clear error state

#### `useAuthState`
Enhanced authentication hook with additional session management features.

**Additional Returns:**
- `sessionInfo`: Session timing information
- `isSessionExpiringSoon`: Whether session expires soon
- `timeUntilExpiry`: Time until token expiry
- `getTimeUntilExpiryFormatted()`: Formatted time string
- `isTokenExpired()`: Check if token is expired
- `getInactivityTime()`: Time since last activity
- `isInactive(threshold)`: Check if user is inactive

## Context

### `AuthContext`
React context providing authentication state management with useReducer.

**State:**
- `user`: User information
- `token`: JWT token
- `isAuthenticated`: Authentication status
- `isLoading`: Loading state
- `error`: Error message

**Actions:**
- `LOGIN_START`: Start login process
- `LOGIN_SUCCESS`: Successful login
- `LOGIN_FAILURE`: Failed login
- `LOGOUT`: User logout
- `SET_LOADING`: Update loading state
- `CLEAR_ERROR`: Clear error state
- `UPDATE_USER`: Update user information

## Services

### `sessionService.js`
Service for managing JWT tokens and session lifecycle.

**Methods:**
- `init(onExpired, onWarning)`: Initialize session management
- `setupTokenRefresh(token, onWarning)`: Set up automatic token refresh
- `refreshToken()`: Refresh current token
- `verifySession()`: Verify session validity
- `getToken()`: Get current token
- `setToken(token, onWarning)`: Set new token
- `clearSession()`: Clear current session
- `getUserFromToken()`: Extract user info from token

## Setup Instructions

### 1. Environment Variables

**Backend (.env):**
```env
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_CALLBACK_URL=http://localhost:5000/api/auth/google/callback
JWT_SECRET=your_secure_jwt_secret
```

**Frontend (.env):**
```env
REACT_APP_GOOGLE_CLIENT_ID=your_google_oauth_client_id
REACT_APP_API_URL=http://localhost:5000/api
```

### 2. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 Client ID
5. Configure authorized origins and redirect URIs
6. Copy client ID and secret to environment variables

### 3. Integration

```jsx
// App.js
import { AuthProvider } from './components/auth';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/protected" element={
            <ProtectedRoute>
              <ProtectedPage />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
```

## Security Features

### Token Management
- Automatic token refresh before expiration
- Secure token storage in localStorage
- Token validation on app initialization
- Automatic logout on token expiration

### Session Management
- Inactivity detection
- Session timeout warnings
- Automatic session extension
- Activity tracking

### Error Handling
- Comprehensive error states
- User-friendly error messages
- Automatic error recovery
- Fallback authentication flows

## Testing

### AuthTest Component
Comprehensive testing component for verifying authentication functionality.

**Features:**
- Authentication state testing
- User profile component testing
- Protected content testing
- Session information display
- Token refresh testing

**Usage:**
```jsx
// Add to your routes for testing
<Route path="/auth-test" element={<AuthTest />} />
```

## Best Practices

### 1. Error Handling
Always handle authentication errors gracefully:

```jsx
const { login, error, clearError } = useAuth();

const handleLogin = async (googleToken) => {
  try {
    const result = await login(googleToken);
    if (!result.success) {
      // Handle login failure
      console.error('Login failed:', result.error);
    }
  } catch (error) {
    // Handle unexpected errors
    console.error('Unexpected error:', error);
  }
};
```

### 2. Protected Routes
Use ProtectedRoute for pages requiring authentication:

```jsx
<ProtectedRoute redirectTo="/login">
  <UserDashboard />
</ProtectedRoute>
```

### 3. Conditional Rendering
Use AuthGuard for conditional content:

```jsx
<AuthGuard requireAuth={true}>
  <PremiumFeatures />
</AuthGuard>

<AuthGuard requireAuth={false}>
  <PublicContent />
</AuthGuard>
```

### 4. Session Management
Monitor session state for better UX:

```jsx
const { isSessionExpiringSoon, refreshToken } = useAuthState();

useEffect(() => {
  if (isSessionExpiringSoon) {
    // Show warning or auto-refresh
    refreshToken();
  }
}, [isSessionExpiringSoon]);
```

## API Integration

### Backend Endpoints
The authentication system expects these backend endpoints:

- `POST /api/auth/google` - Google OAuth verification
- `GET /api/auth/user` - Get current user
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/session` - Check session validity

### Request Headers
Authenticated requests should include:

```javascript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

## Troubleshooting

### Common Issues

1. **"Google Client ID not configured"**
   - Check REACT_APP_GOOGLE_CLIENT_ID in .env
   - Verify environment variable is loaded

2. **"Authentication failed"**
   - Check backend is running
   - Verify API URL in environment variables
   - Check network connectivity

3. **"Token expired"**
   - Implement automatic token refresh
   - Check JWT secret configuration
   - Verify token expiration settings

4. **"Session timeout"**
   - Implement session warning system
   - Allow users to extend sessions
   - Provide clear logout options

### Debug Mode
Enable debug logging by setting:

```javascript
localStorage.setItem('auth_debug', 'true');
```

This will log authentication events to the console for debugging purposes.