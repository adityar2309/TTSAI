# TTSAI Authentication Setup Guide

This guide walks you through setting up Google OAuth authentication for the TTSAI application.

## Prerequisites

1. **Google Cloud Console Access**: You need access to Google Cloud Console to create OAuth credentials
2. **Node.js and npm**: For frontend development
3. **Python 3.8+**: For backend development
4. **Google Cloud CLI**: For backend deployment
5. **Netlify CLI**: For frontend deployment

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
# Windows
setup_and_deploy.bat

# Linux/Mac
chmod +x setup_and_deploy.sh
./setup_and_deploy.sh
```

This script will:
1. Guide you through OAuth credential setup
2. Test the authentication integration
3. Deploy both backend and frontend

### Option 2: Manual Setup

#### Step 1: Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google+ API
   - Google Identity API
4. Go to **Credentials** > **Create Credentials** > **OAuth 2.0 Client ID**
5. Set application type to **Web application**
6. Configure authorized origins:
   - Development: `http://localhost:3000`
   - Production: `https://your-netlify-domain.netlify.app`
7. Configure authorized redirect URIs:
   - Development: `http://localhost:5000/api/auth/google/callback`
   - Production: `https://your-backend-domain/api/auth/google/callback`

#### Step 2: Configure Environment Variables

Run the OAuth setup script:

```bash
python setup_google_oauth.py
```

Or manually update the environment files:

**Backend (.env):**
```env
GOOGLE_CLIENT_ID="your_actual_client_id"
GOOGLE_CLIENT_SECRET="your_actual_client_secret"
JWT_SECRET="your_secure_jwt_secret"
```

**Frontend (.env):**
```env
REACT_APP_GOOGLE_CLIENT_ID="your_actual_client_id"
```

#### Step 3: Test Authentication

```bash
python test_auth_integration.py
```

#### Step 4: Deploy

```bash
python deploy_with_auth.py
```

## Architecture Overview

### Backend Authentication Flow

1. **Google Token Verification**: Frontend sends Google ID token to `/api/auth/google`
2. **User Creation/Update**: Backend verifies token and creates/updates user in database
3. **JWT Generation**: Backend generates JWT token for session management
4. **Protected Routes**: Routes use `@token_required` decorator for authentication

### Frontend Authentication Flow

1. **Google OAuth**: User signs in with Google using `@react-oauth/google`
2. **Token Exchange**: Frontend sends Google token to backend
3. **Session Management**: Frontend stores JWT token and manages user state
4. **Route Protection**: Protected routes check authentication status

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    google_id TEXT UNIQUE,
    name TEXT,
    email TEXT UNIQUE,
    profile_picture TEXT,
    created_at TEXT,
    updated_at TEXT,
    last_login TEXT
);

-- User sessions table
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    token TEXT,
    created_at TEXT,
    expires_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/google` - Authenticate with Google token
- `GET /api/auth/user` - Get current user info (requires auth)
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/session` - Check session validity (requires auth)
- `POST /api/auth/refresh` - Refresh JWT token (requires auth)

### Example Usage

```javascript
// Frontend - Sign in with Google
const handleGoogleSuccess = async (credentialResponse) => {
  const response = await fetch('/api/auth/google', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: credentialResponse.credential })
  });
  
  const data = await response.json();
  // Store JWT token and user data
};

// Frontend - Make authenticated request
const fetchUserData = async () => {
  const response = await fetch('/api/auth/user', {
    headers: { 
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}` 
    }
  });
  
  return response.json();
};
```

## Components Overview

### Backend Components

- **`auth_service.py`**: Core authentication logic
- **`auth_routes.py`**: Authentication API endpoints
- **`auth_config.py`**: Authentication configuration
- **`db_service_auth.py`**: Database operations for auth
- **`models.py`**: User and session models

### Frontend Components

- **`AuthContext.js`**: React context for auth state management
- **`LoginPage.js`**: Login page component
- **`GoogleSignInButton.js`**: Google OAuth button component
- **`UserProfile.js`**: User profile display component
- **`AuthGuard.js`**: Route protection component
- **`ProtectedRoute.js`**: Protected route wrapper

## Security Features

1. **JWT Token Security**: Secure token generation with expiration
2. **Google OAuth Verification**: Server-side token verification
3. **CORS Protection**: Configured for specific origins
4. **Session Management**: Automatic token refresh and cleanup
5. **Input Validation**: Comprehensive input validation and sanitization

## Troubleshooting

### Common Issues

1. **"Google Client ID not found"**
   - Run `python setup_google_oauth.py`
   - Check environment variables are properly set

2. **CORS Errors**
   - Verify authorized origins in Google Console
   - Check CORS configuration in `backend/app.py`

3. **Token Verification Failed**
   - Ensure Google+ API is enabled
   - Check client ID matches between frontend and backend

4. **Database Errors**
   - Run `python test_auth_integration.py` to test database
   - Check SQLite database permissions

### Debug Mode

Enable debug logging in backend:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Authentication

```bash
# Test backend health
curl http://localhost:5000/health

# Test auth endpoint (should return 400 - missing token)
curl -X POST http://localhost:5000/api/auth/google

# Test protected endpoint (should return 401 - unauthorized)
curl http://localhost:5000/api/auth/user
```

## Production Deployment

### Backend (Google Cloud Run)

1. Update production environment variables
2. Deploy with: `gcloud run deploy ttsai-backend --source backend`
3. Update CORS origins for production domain

### Frontend (Netlify)

1. Update production environment variables
2. Build: `npm run build`
3. Deploy: `netlify deploy --prod --dir=build`

### Environment Variables for Production

**Backend:**
```env
FLASK_ENV=production
GOOGLE_CALLBACK_URL=https://your-backend-domain/api/auth/google/callback
```

**Frontend:**
```env
REACT_APP_API_URL=https://your-backend-domain/api
```

## Monitoring and Analytics

The authentication system includes:

- User login/logout tracking
- Session duration monitoring
- Failed authentication attempts logging
- User activity analytics

## Support

For issues or questions:

1. Check this guide first
2. Run the test script: `python test_auth_integration.py`
3. Check application logs
4. Review Google Cloud Console for OAuth issues

## Security Considerations

1. **Never commit credentials** to version control
2. **Use HTTPS** in production
3. **Regularly rotate** JWT secrets
4. **Monitor** authentication logs
5. **Keep dependencies** updated

## License

This authentication system is part of the TTSAI project and follows the same license terms.