import React from 'react';
import { Box, Typography, Paper, CircularProgress } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import GoogleSignInButton from './GoogleSignInButton';

const AuthGuard = ({ 
  children, 
  fallback,
  requireAuth = true,
  loadingComponent,
  title = "Sign in to continue",
  subtitle = "Access your personalized learning experience"
}) => {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading state
  if (isLoading) {
    if (loadingComponent) {
      return loadingComponent;
    }
    
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '200px',
          flexDirection: 'column',
          gap: 2
        }}
      >
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Loading...
        </Typography>
      </Box>
    );
  }

  // If authentication is required and user is not authenticated
  if (requireAuth && !isAuthenticated) {
    if (fallback) {
      return fallback;
    }

    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '400px',
          p: 3
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            maxWidth: 400,
            width: '100%',
            textAlign: 'center'
          }}
        >
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {subtitle}
          </Typography>

          <GoogleSignInButton
            fullWidth
            text="Sign in with Google"
            onSuccess={(user) => {
              console.log('User signed in:', user);
            }}
            onError={(error) => {
              console.error('Sign in error:', error);
            }}
          />

          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            By signing in, you agree to our Terms of Service and Privacy Policy
          </Typography>
        </Paper>
      </Box>
    );
  }

  // If authentication is not required or user is authenticated
  return children;
};

export default AuthGuard;