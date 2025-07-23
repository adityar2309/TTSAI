import React from 'react';
import { Box, Paper, Typography, Container } from '@mui/material';
import GoogleSignInButton from './GoogleSignInButton';
import UserProfile from './UserProfile';
import { useAuth } from '../../contexts/AuthContext';

const AuthWrapper = ({ children, requireAuth = false, redirectPath = '/' }) => {
  const { isAuthenticated, loading } = useAuth();

  // If authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated && !loading) {
    return (
      <Container maxWidth="sm" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom align="center">
            Authentication Required
          </Typography>
          <Typography variant="body1" paragraph align="center">
            Please sign in to access this feature.
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <GoogleSignInButton />
          </Box>
        </Paper>
      </Container>
    );
  }

  // If loading, show nothing (loading state should be handled by parent components)
  if (loading) {
    return null;
  }

  // Otherwise, render children
  return <>{children}</>;
};

export default AuthWrapper;