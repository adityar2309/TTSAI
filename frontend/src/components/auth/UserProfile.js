import React, { useState } from 'react';
import {
  Box,
  Avatar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon,
  ListItemText,
  Chip,
  Tooltip,
  Button
} from '@mui/material';
import {
  AccountCircle,
  Settings,
  Logout,
  ExpandMore,
  Person,
  Email,
  Schedule
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { formatDistanceToNow } from 'date-fns';

const UserProfile = ({ 
  variant = 'menu', // 'menu', 'card', 'minimal'
  showLastLogin = true,
  onSettingsClick,
  onProfileClick
}) => {
  const { user, logout, isAuthenticated } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    setIsLoggingOut(true);
    handleMenuClose();
    
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleSettings = () => {
    handleMenuClose();
    if (onSettingsClick) {
      onSettingsClick();
    }
  };

  const handleProfile = () => {
    handleMenuClose();
    if (onProfileClick) {
      onProfileClick();
    }
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  // Minimal variant - just avatar and name
  if (variant === 'minimal') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Avatar
          src={user.profilePicture || user.picture}
          alt={user.name}
          sx={{ width: 32, height: 32 }}
        >
          {user.name?.charAt(0).toUpperCase()}
        </Avatar>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {user.name}
        </Typography>
      </Box>
    );
  }

  // Card variant - expanded profile info
  if (variant === 'card') {
    return (
      <Box
        sx={{
          p: 2,
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 2,
          backgroundColor: 'background.paper'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Avatar
            src={user.profilePicture || user.picture}
            alt={user.name}
            sx={{ width: 56, height: 56 }}
          >
            {user.name?.charAt(0).toUpperCase()}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {user.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {user.email}
            </Typography>
          </Box>
        </Box>

        {showLastLogin && user.lastLogin && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Schedule sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              Last login: {formatDistanceToNow(new Date(user.lastLogin), { addSuffix: true })}
            </Typography>
          </Box>
        )}

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            size="small"
            startIcon={<Settings />}
            onClick={handleSettings}
          >
            Settings
          </Button>
          <Button
            size="small"
            startIcon={<Logout />}
            onClick={handleLogout}
            disabled={isLoggingOut}
            color="error"
          >
            {isLoggingOut ? 'Signing out...' : 'Sign out'}
          </Button>
        </Box>
      </Box>
    );
  }

  // Default menu variant
  return (
    <Box>
      <Tooltip title="Account">
        <IconButton
          onClick={handleMenuOpen}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            px: 1,
            borderRadius: 2
          }}
        >
          <Avatar
            src={user.profilePicture || user.picture}
            alt={user.name}
            sx={{ width: 32, height: 32 }}
          >
            {user.name?.charAt(0).toUpperCase()}
          </Avatar>
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              {user.name}
            </Typography>
          </Box>
          <ExpandMore sx={{ fontSize: 16 }} />
        </IconButton>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        onClick={handleMenuClose}
        PaperProps={{
          elevation: 3,
          sx: {
            minWidth: 280,
            mt: 1.5,
            '& .MuiMenuItem-root': {
              px: 2,
              py: 1
            }
          }
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        {/* User Info Header */}
        <Box sx={{ px: 2, py: 1.5, backgroundColor: 'grey.50' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar
              src={user.profilePicture || user.picture}
              alt={user.name}
              sx={{ width: 40, height: 40 }}
            >
              {user.name?.charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                {user.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user.email}
              </Typography>
            </Box>
          </Box>
          
          {showLastLogin && user.lastLogin && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Last login: {formatDistanceToNow(new Date(user.lastLogin), { addSuffix: true })}
            </Typography>
          )}
        </Box>

        <Divider />

        {/* Menu Items */}
        <MenuItem onClick={handleProfile}>
          <ListItemIcon>
            <Person fontSize="small" />
          </ListItemIcon>
          <ListItemText>Profile</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleSettings}>
          <ListItemIcon>
            <Settings fontSize="small" />
          </ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>

        <Divider />

        <MenuItem onClick={handleLogout} disabled={isLoggingOut}>
          <ListItemIcon>
            <Logout fontSize="small" color={isLoggingOut ? 'disabled' : 'error'} />
          </ListItemIcon>
          <ListItemText>
            <Typography color={isLoggingOut ? 'text.disabled' : 'error'}>
              {isLoggingOut ? 'Signing out...' : 'Sign out'}
            </Typography>
          </ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default UserProfile;