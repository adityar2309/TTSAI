import React, { useState } from 'react';
import { Box, Typography, Paper, Button, Alert, Grid, Divider } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import GoogleSignInButton from './GoogleSignInButton';
import UserProfile from './UserProfile';
import AuthStatus from './AuthStatus';
import AuthGuard from './AuthGuard';
import useAuthState from './useAuthState';

const AuthTest = () => {
  const { isAuthenticated, user, isLoading, error, logout } = useAuth();
  const authState = useAuthState();
  const [testResults, setTestResults] = useState([]);

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Loading authentication state...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Authentication Test
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Authentication Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Authentication Status
            </Typography>
            <AuthStatus variant="detailed" />
            
            {isAuthenticated && (
              <Box sx={{ mt: 2 }}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  Session Information:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Time until expiry: {authState.getTimeUntilExpiryFormatted() || 'Unknown'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Is expiring soon: {authState.isSessionExpiringSoon ? 'Yes' : 'No'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Last activity: {new Date(authState.lastActivity).toLocaleTimeString()}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* User Profile Variants */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              User Profile Components
            </Typography>
            
            {isAuthenticated ? (
              <Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Minimal Variant:
                  </Typography>
                  <UserProfile variant="minimal" />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Compact Variant:
                  </Typography>
                  <UserProfile variant="menu" />
                </Box>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Sign in to view profile components
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Sign In / Protected Content Test */}
      <Box sx={{ mt: 3 }}>
        {!isAuthenticated ? (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Sign In Test
            </Typography>
            <GoogleSignInButton
              fullWidth
              onSuccess={(user) => {
                console.log('Sign in successful:', user);
              }}
              onError={(error) => {
                console.error('Sign in error:', error);
              }}
            />
          </Paper>
        ) : (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Protected Content Test
            </Typography>
            
            <AuthGuard
              title="Protected Section"
              subtitle="This content requires authentication"
            >
              <Alert severity="success" sx={{ mb: 2 }}>
                🎉 You can see this content because you are authenticated!
              </Alert>
              
              <Typography variant="body1" sx={{ mb: 2 }}>
                Welcome, {user?.name}! This is a protected section that only
                authenticated users can access.
              </Typography>
              
              <Button
                variant="outlined"
                color="error"
                onClick={logout}
              >
                Test Logout
              </Button>
            </AuthGuard>
          </Paper>
        )}
      </Box>
    </Box>
  );
};

export default AuthTest;