import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';

const ProtectedRoute = ({ 
  children, 
  redirectTo = '/login',
  requireAuth = true,
  fallback,
  loadingComponent
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Show custom loading component or default
  if (isLoading) {
    if (loadingComponent) {
      return loadingComponent;
    }
    
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '50vh',
          gap: 2
        }}
      >
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Verifying authentication...
        </Typography>
      </Box>
    );
  }

  // If authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    // Show custom fallback or redirect to login
    if (fallback) {
      return fallback;
    }
    
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // If authentication is not required or user is authenticated
  return children;
};

export default ProtectedRoute;