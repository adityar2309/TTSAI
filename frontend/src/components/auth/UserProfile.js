import React, { useState } from 'react';
import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  IconButton,
  Menu,
  MenuItem,
  Typography
} from '@mui/material';
import {
  AccountCircle,
  Logout,
  Settings,
  ExpandMore,
  Language,
  School,
  EmojiEvents
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const UserProfile = () => {
  const { user, logout, loading } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [expanded, setExpanded] = useState(false);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
  };

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <Card sx={{ mb: 3, overflow: 'visible' }}>
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar
              src={user.profilePicture}
              alt={user.name}
              sx={{ width: 48, height: 48, mr: 2 }}
            />
            <Box>
              <Typography variant="h6" component="div">
                {user.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {user.email}
              </Typography>
            </Box>
          </Box>

          <IconButton
            aria-label="account menu"
            aria-controls="user-menu"
            aria-haspopup="true"
            onClick={handleMenuOpen}
          >
            <AccountCircle />
          </IconButton>
          <Menu
            id="user-menu"
            anchorEl={anchorEl}
            keepMounted
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleMenuClose}>
              <Settings fontSize="small" sx={{ mr: 1 }} /> Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <Logout fontSize="small" sx={{ mr: 1 }} /> Logout
            </MenuItem>
          </Menu>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Level
              </Typography>
              <Typography variant="h6">5</Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                XP
              </Typography>
              <Typography variant="h6">1250</Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Streak
              </Typography>
              <Typography variant="h6">7</Typography>
            </Box>
          </Box>

          <IconButton
            onClick={handleExpandClick}
            aria-expanded={expanded}
            aria-label="show more"
          >
            <ExpandMore sx={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s' }} />
          </IconButton>
        </Box>

        {expanded && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Learning Progress
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Language sx={{ mr: 0.5, color: 'primary.main' }} fontSize="small" />
                <Typography variant="body2">3 Languages</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <School sx={{ mr: 0.5, color: 'primary.main' }} fontSize="small" />
                <Typography variant="body2">12 Quizzes</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <EmojiEvents sx={{ mr: 0.5, color: 'primary.main' }} fontSize="small" />
                <Typography variant="body2">5 Achievements</Typography>
              </Box>
            </Box>
            <Button variant="outlined" size="small" fullWidth>
              View Full Profile
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default UserProfile;