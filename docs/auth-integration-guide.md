# Authentication Integration Guide

This guide explains how to integrate the Google OAuth authentication service into the main Flask application.

## Prerequisites

1. Google OAuth credentials (see `docs/google-oauth-setup.md`)
2. Updated environment variables in `.env` files

## Installation Steps

1. Install required Python packages:

```bash
cd backend
pip install -r requirements-auth.txt
```

2. Integrate authentication into the main app.py file:

Add the following imports at the top of `app.py`:

```python
# Authentication imports
from auth_integration import integrate_auth
```

Add the following code after initializing the Flask app and database service:

```python
# Integrate authentication
app = integrate_auth(app, db_service)
```

## Testing Authentication

1. Run the authentication tests:

```bash
cd backend
python test_auth.py
```

2. Verify that all endpoints are available and responding correctly.

## Authentication Flow

1. **Frontend**: User clicks "Sign in with Google" button
2. **Frontend**: Google OAuth popup appears and user authenticates
3. **Frontend**: Google returns ID token to frontend
4. **Frontend**: Frontend sends ID token to backend `/api/auth/google` endpoint
5. **Backend**: Verifies token with Google
6. **Backend**: Creates or updates user in database
7. **Backend**: Generates JWT token
8. **Backend**: Returns JWT token to frontend
9. **Frontend**: Stores JWT token in localStorage
10. **Frontend**: Uses JWT token for authenticated requests

## Protected Routes

To protect a route in the backend, use the `token_required` decorator:

```python
from auth_routes import token_required

@app.route('/api/protected-route', methods=['GET'])
@token_required
def protected_route():
    # Access user info from request.user
    user_id = request.user['sub']
    return jsonify({'message': f'Hello, user {user_id}!'})
```

## Frontend Authentication

In the frontend, add the authentication token to API requests:

```javascript
const apiCall = async (endpoint, method = 'GET', data = null) => {
  const token = localStorage.getItem('authToken');
  
  const headers = {
    'Content-Type': 'application/json'
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const options = {
    method,
    headers
  };
  
  if (data) {
    options.body = JSON.stringify(data);
  }
  
  const response = await fetch(`${API_URL}/${endpoint}`, options);
  return response.json();
};
```

## Session Management

The authentication service includes session management features:

- JWT tokens expire after 24 hours (configurable in `auth_config.py`)
- Use the `/api/auth/refresh` endpoint to refresh tokens before they expire
- Use the `/api/auth/logout` endpoint to log out users
- Use the `/api/auth/session` endpoint to check if a session is valid

## Security Considerations

1. Always use HTTPS in production
2. Store JWT tokens securely (HTTP-only cookies in production)
3. Implement CSRF protection
4. Regularly rotate JWT secrets
5. Limit token permissions to only what's needed
6. Implement rate limiting for authentication endpoints