import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { Button, Box, Typography, Alert, CircularProgress } from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const GoogleSignInButton = ({ 
  onSuccess, 
  onError, 
  variant = 'contained',
  size = 'large',
  fullWidth = false,
  disabled = false,
  text = 'Sign in with Google'
}) => {
  const { login, isLoading, error } = useAuth();
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState(null);

  const handleSuccess = async (credentialResponse) => {
    setLocalLoading(true);
    setLocalError(null);

    try {
      const result = await login(credentialResponse.credential);
      
      if (result.success) {
        if (onSuccess) {
          onSuccess(result.user);
        }
      } else {
        setLocalError(result.error || 'Authentication failed');
        if (onError) {
          onError(result.error);
        }
      }
    } catch (error) {
      const errorMessage = error.message || 'An unexpected error occurred';
      setLocalError(errorMessage);
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setLocalLoading(false);
    }
  };

  const handleError = () => {
    const errorMessage = 'Google authentication was cancelled or failed';
    setLocalError(errorMessage);
    if (onError) {
      onError(errorMessage);
    }
  };

  const isButtonDisabled = disabled || isLoading || localLoading;
  const displayError = error || localError;

  return (
    <Box sx={{ width: fullWidth ? '100%' : 'auto' }}>
      {displayError && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          onClose={() => {
            setLocalError(null);
          }}
        >
          {displayError}
        </Alert>
      )}
      
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={handleError}
        useOneTap={false}
        auto_select={false}
        render={({ onClick, disabled: googleDisabled }) => (
          <Button
            variant={variant}
            size={size}
            fullWidth={fullWidth}
            disabled={isButtonDisabled || googleDisabled}
            onClick={onClick}
            startIcon={
              localLoading || isLoading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <GoogleIcon />
              )
            }
            sx={{
              textTransform: 'none',
              py: 1.5,
              px: 3,
              backgroundColor: variant === 'contained' ? '#4285f4' : 'transparent',
              color: variant === 'contained' ? 'white' : '#4285f4',
              border: variant === 'outlined' ? '1px solid #4285f4' : 'none',
              '&:hover': {
                backgroundColor: variant === 'contained' ? '#3367d6' : 'rgba(66, 133, 244, 0.04)',
              },
              '&:disabled': {
                backgroundColor: variant === 'contained' ? '#cccccc' : 'transparent',
                color: '#999999',
              }
            }}
          >
            <Typography variant="button" sx={{ ml: 1 }}>
              {localLoading || isLoading ? 'Signing in...' : text}
            </Typography>
          </Button>
        )}
      />
    </Box>
  );
};

export default GoogleSignInButton;