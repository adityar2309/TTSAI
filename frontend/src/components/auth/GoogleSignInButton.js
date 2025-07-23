import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { Box, Typography, Alert, CircularProgress } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';

const GoogleSignInButton = ({ onSuccess }) => {
  const { handleGoogleLogin, loading, error, clearError } = useAuth();

  const handleSuccess = async (credentialResponse) => {
    const success = await handleGoogleLogin(credentialResponse);
    if (success && onSuccess) {
      onSuccess();
    }
  };

  const handleError = () => {
    console.error('Google Sign In Failed');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      {error && (
        <Alert severity="error" onClose={clearError} sx={{ width: '100%' }}>
          {error}
        </Alert>
      )}
      
      {loading ? (
        <CircularProgress size={24} />
      ) : (
        <>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 1 }}>
            Sign in with your Google account to access personalized features
          </Typography>
          
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={handleError}
            useOneTap
            shape="rectangular"
            theme="filled_blue"
            text="signin_with"
            size="large"
          />
        </>
      )}
    </Box>
  );
};

export default GoogleSignInButton;