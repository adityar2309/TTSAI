# Setting Up Google OAuth Credentials

This guide walks through the process of creating Google OAuth credentials for the application.

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

## Steps to Create Google OAuth Credentials

### 1. Create a New Project (or select an existing one)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Speech Translator App")
5. Click "Create"

### 2. Enable the Google OAuth API

1. Select your project from the dashboard
2. Navigate to "APIs & Services" > "Library" from the left sidebar
3. Search for "Google OAuth2 API" or "Google Identity"
4. Click on "Google Identity Services" or "OAuth 2.0" API
5. Click "Enable"

### 3. Configure the OAuth Consent Screen

1. Navigate to "APIs & Services" > "OAuth consent screen" from the left sidebar
2. Select the appropriate user type:
   - "External" if you want anyone with a Google account to be able to use your app
   - "Internal" if you're only allowing users within your organization
3. Click "Create"
4. Fill in the required information:
   - App name: "Speech Translator"
   - User support email: Your email address
   - Developer contact information: Your email address
5. Click "Save and Continue"
6. Add the following scopes:
   - `./auth/userinfo.email`
   - `./auth/userinfo.profile`
   - `openid`
7. Click "Save and Continue"
8. Add any test users if needed (for external user type)
9. Click "Save and Continue"
10. Review your settings and click "Back to Dashboard"

### 4. Create OAuth Client ID

1. Navigate to "APIs & Services" > "Credentials" from the left sidebar
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application" as the application type
4. Name: "Speech Translator Web Client"
5. Add authorized JavaScript origins:
   - `http://localhost:3000` (for local development)
   - `https://ttsai.netlify.app` (for production)
6. Add authorized redirect URIs:
   - `http://localhost:3000/auth/google/callback` (for local development)
   - `https://ttsai.netlify.app/auth/google/callback` (for production)
7. Click "Create"

### 5. Save Your Credentials

After creating the client ID, you'll see a modal with your client ID and client secret:

1. Download the JSON file for safekeeping
2. Note down the Client ID and Client Secret to add to your environment variables

## Adding Credentials to Environment Variables

### Backend (.env)

Add the following to your backend `.env` file:

```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_CALLBACK_URL=http://localhost:5000/api/auth/google/callback
JWT_SECRET=generate_a_secure_random_string_here
```

For production, update the callback URL accordingly.

### Frontend (.env)

Add the following to your frontend `.env` file:

```
REACT_APP_GOOGLE_CLIENT_ID=your_client_id_here
```

## Security Notes

- Never commit your client secret to version control
- Use environment variables to store sensitive credentials
- Regularly rotate your client secret for enhanced security
- Limit the scopes requested to only what your application needs