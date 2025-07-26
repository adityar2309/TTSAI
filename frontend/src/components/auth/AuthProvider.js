import React, { useState, useEffect } from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AuthProvider as AuthContextProvider } from '../../contexts/AuthContext';
import SessionTimeoutWarning from './SessionTimeoutWarning';
import { Alert, Snackbar, Box, CircularProgress, Typography } from '@mui/material';

const AuthProvider = ({ children }) => {
  const [authError, setAuthError] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [showSessionWarning, setShowSessionWarning] = useState(false);

  const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

  useEffect(() => {
    // Simulate initialization delay
    const timer = setTimeout(() => {
      setIsInitializing(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleAuthError = (error) => {
    setAuthError(error);
  };

  const handleCloseError = () => {
    setAuthError(null);
  };

  const handleSessionWarning = () => {
    setShowSessionWarning(true);
  };

  const handleCloseSessionWarning = () => {
    setShowSessionWarning(false);
  };

  // Show loading screen during initialization
  if (isInitializing) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          gap: 2
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="h6" color="text.secondary">
          Initializing application...
        </Typography>
      </Box>
    );
  }

  // Show error if Google Client ID is not configured
  if (!googleClientId) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          p: 3
        }}
      >
        <Alert severity="error" sx={{ maxWidth: 600 }}>
          <Typography variant="h6" gutterBottom>
            Configuration Error
          </Typography>
          <Typography variant="body1">
            Google OAuth client ID is not configured. Please check your environment variables.
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            Make sure <code>REACT_APP_GOOGLE_CLIENT_ID</code> is set in your .env file.
          </Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthContextProvider onError={handleAuthError}>
        {children}
        
        {/* Session timeout warning */}
        <SessionTimeoutWarning />
        
        {/* Global auth error snackbar */}
        <Snackbar
          open={!!authError}
          autoHideDuration={6000}
          onClose={handleCloseError}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleCloseError} 
            severity="error" 
            variant="filled"
            sx={{ width: '100%' }}
          >
            Authentication Error: {authError}
          </Alert>
        </Snackbar>
      </AuthContextProvider>
    </GoogleOAuthProvider>
  );
};

export default AuthProvider;