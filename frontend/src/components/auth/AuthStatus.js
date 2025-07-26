import React from 'react';
import {
  Box,
  Chip,
  Typography,
  Avatar,
  Tooltip,
  IconButton,
  Alert,
  Skeleton
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Refresh,
  Logout
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { formatDistanceToNow } from 'date-fns';

const AuthStatus = ({ 
  variant = 'compact', // 'compact', 'detailed', 'minimal'
  showActions = true,
  showLastLogin = true,
  onRefresh,
  onLogout
}) => {
  const { 
    user, 
    isAuthenticated, 
    isLoading, 
    error, 
    refreshToken, 
    logout,
    clearError 
  } = useAuth();

  const handleRefresh = async () => {
    if (onRefresh) {
      onRefresh();
    } else {
      await refreshToken();
    }
  };

  const handleLogout = async () => {
    if (onLogout) {
      onLogout();
    } else {
      await logout();
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Skeleton variant="circular" width={32} height={32} />
        <Box>
          <Skeleton variant="text" width={120} height={20} />
          <Skeleton variant="text" width={80} height={16} />
        </Box>
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert 
        severity="error" 
        variant="outlined"
        onClose={clearError}
        action={
          showActions && (
            <IconButton
              color="inherit"
              size="small"
              onClick={handleRefresh}
            >
              <Refresh />
            </IconButton>
          )
        }
      >
        Authentication Error: {error}
      </Alert>
    );
  }

  // Not authenticated
  if (!isAuthenticated || !user) {
    return (
      <Chip
        icon={<Warning />}
        label="Not signed in"
        color="warning"
        variant="outlined"
        size="small"
      />
    );
  }

  // Minimal variant
  if (variant === 'minimal') {
    return (
      <Chip
        avatar={
          <Avatar 
            src={user.profilePicture || user.picture} 
            sx={{ width: 24, height: 24 }}
          >
            {user.name?.charAt(0).toUpperCase()}
          </Avatar>
        }
        label={user.name}
        color="success"
        variant="outlined"
        size="small"
      />
    );
  }

  // Compact variant
  if (variant === 'compact') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Tooltip title="Authenticated">
          <CheckCircle color="success" sx={{ fontSize: 16 }} />
        </Tooltip>
        
        <Avatar
          src={user.profilePicture || user.picture}
          alt={user.name}
          sx={{ width: 24, height: 24 }}
        >
          {user.name?.charAt(0).toUpperCase()}
        </Avatar>
        
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {user.name}
        </Typography>

        {showActions && (
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title="Refresh session">
              <IconButton size="small" onClick={handleRefresh}>
                <Refresh sx={{ fontSize: 16 }} />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Sign out">
              <IconButton size="small" onClick={handleLogout} color="error">
                <Logout sx={{ fontSize: 16 }} />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Box>
    );
  }

  // Detailed variant
  return (
    <Box
      sx={{
        p: 2,
        border: '1px solid',
        borderColor: 'success.main',
        borderRadius: 2,
        backgroundColor: 'success.50'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <Avatar
          src={user.profilePicture || user.picture}
          alt={user.name}
          sx={{ width: 40, height: 40 }}
        >
          {user.name?.charAt(0).toUpperCase()}
        </Avatar>
        
        <Box sx={{ flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              {user.name}
            </Typography>
            <Chip
              icon={<CheckCircle />}
              label="Authenticated"
              color="success"
              size="small"
              variant="outlined"
            />
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            {user.email}
          </Typography>
        </Box>

        {showActions && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Refresh session">
              <IconButton size="small" onClick={handleRefresh}>
                <Refresh />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Sign out">
              <IconButton size="small" onClick={handleLogout} color="error">
                <Logout />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Box>

      {showLastLogin && user.lastLogin && (
        <Typography variant="caption" color="text.secondary">
          Last login: {formatDistanceToNow(new Date(user.lastLogin), { addSuffix: true })}
        </Typography>
      )}
    </Box>
  );
};

export default AuthStatus;