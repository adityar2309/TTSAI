# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for the learning tools application.

## Prerequisites

- Google account
- Access to Google Cloud Console

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter project name (e.g., "Learning Tools App")
5. Click "Create"

### 2. Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - **Google+ API** (for user profile information)
   - **Google Identity and Access Management (IAM) API**

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace)
3. Fill in the required information:
   - **App name**: Learning Tools App
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. Click "Save and Continue"
5. Add scopes (click "Add or Remove Scopes"):
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
   - `openid`
6. Click "Save and Continue"
7. Add test users (your email and any other emails you want to test with)
8. Click "Save and Continue"

### 4. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Choose "Web application" as application type
4. Enter name: "Learning Tools Web Client"
5. Add **Authorized JavaScript origins**:
   - `http://localhost:3000` (for development)
   - Add your production domain when deploying
6. Add **Authorized redirect URIs**:
   - `http://localhost:5000/api/auth/google/callback` (for development)
   - Add your production callback URL when deploying
7. Click "Create"

### 5. Copy Credentials

After creating the OAuth client, you'll see a dialog with:
- **Client ID**: Copy this value
- **Client Secret**: Copy this value

### 6. Update Environment Variables

#### Backend (.env file)
```env
GOOGLE_CLIENT_ID="your_client_id_here"
GOOGLE_CLIENT_SECRET="your_client_secret_here"
```

#### Frontend (.env file)
```env
REACT_APP_GOOGLE_CLIENT_ID="your_client_id_here"
```

**Note**: Use the same Client ID for both backend and frontend.

### 7. Generate JWT Secret

Generate a secure JWT secret for token signing:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Update the backend `.env` file:
```env
JWT_SECRET="your_generated_secret_here"
```

## Testing the Setup

1. Start the backend server: `python app.py`
2. Start the frontend server: `npm start`
3. Navigate to the application
4. Try the "Sign in with Google" button
5. You should be redirected to Google's OAuth consent screen

## Troubleshooting

### Common Issues

1. **"Error 400: redirect_uri_mismatch"**
   - Check that your redirect URI in Google Console matches exactly: `http://localhost:5000/api/auth/google/callback`
   - Make sure there are no trailing slashes

2. **"Error 403: access_denied"**
   - Make sure you've added your email as a test user in the OAuth consent screen
   - Check that required scopes are configured

3. **"Invalid client ID"**
   - Verify the client ID is correctly copied to both backend and frontend `.env` files
   - Make sure there are no extra spaces or quotes

4. **CORS errors**
   - Ensure `http://localhost:3000` is added to Authorized JavaScript origins
   - Check that your backend CORS configuration allows the frontend domain

### Production Deployment

When deploying to production:

1. Update Authorized JavaScript origins with your production domain
2. Update Authorized redirect URIs with your production callback URL
3. Update environment variables with production values
4. Consider moving from "Testing" to "In production" status in OAuth consent screen

## Security Notes

- Never commit your `.env` files to version control
- Use different OAuth clients for development and production
- Regularly rotate your JWT secret
- Monitor OAuth usage in Google Cloud Console
- Consider implementing additional security measures like rate limiting

## Support

If you encounter issues:
1. Check the Google Cloud Console error logs
2. Review the browser developer console for client-side errors
3. Check the backend application logs
4. Refer to [Google OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)