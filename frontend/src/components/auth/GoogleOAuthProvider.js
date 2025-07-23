import React from 'react';
import { GoogleOAuthProvider as GoogleProvider } from '@react-oauth/google';
import { AuthProvider } from '../../contexts/AuthContext';

const GoogleOAuthProvider = ({ children }) => {
  const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

  if (!clientId) {
    console.error('Google OAuth client ID is not configured');
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        Error: Google OAuth client ID is not configured.
        Please check your environment variables.
      </div>
    );
  }

  return (
    <GoogleProvider clientId={clientId}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </GoogleProvider>
  );
};

export default GoogleOAuthProvider;