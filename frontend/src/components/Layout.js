import React, { useState } from 'react';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
  useMediaQuery,
  Tooltip,
  Fade,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import TranslateIcon from '@mui/icons-material/Translate';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useNavigate, useLocation } from 'react-router-dom';
import Logo from './Logo';

const Layout = ({ children, toggleColorMode, mode }) => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const menuItems = [
    { text: 'Translator', icon: <TranslateIcon />, path: '/' },
  ];

  const handleNavigation = (path) => {
    navigate(path);
    setDrawerOpen(false);
  };

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        minHeight: '100vh',
        bgcolor: 'background.default',
        transition: theme.transitions.create(['background-color'], {
          duration: theme.transitions.duration.standard,
        }),
      }}
    >
      <AppBar 
        position="fixed"
        elevation={0}
        sx={{
          backdropFilter: 'blur(8px)',
          backgroundColor: mode === 'dark' 
            ? 'rgba(30, 30, 30, 0.8)' 
            : 'rgba(255, 255, 255, 0.8)',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ minHeight: { xs: '56px', sm: '64px' } }}>
          <IconButton
            size={isMobile ? 'medium' : 'large'}
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 1 }}
            onClick={() => setDrawerOpen(true)}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }}>
            <Logo />
          </Box>

          <Tooltip 
            title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}
            TransitionComponent={Fade}
            TransitionProps={{ timeout: 600 }}
          >
            <IconButton
              color="inherit"
              onClick={toggleColorMode}
              sx={{
                transition: theme.transitions.create(['transform', 'color'], {
                  duration: theme.transitions.duration.shorter,
                }),
                '&:hover': {
                  transform: 'rotate(12deg)',
                },
              }}
            >
              {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: isMobile ? '80%' : 250,
            maxWidth: 300,
            bgcolor: 'background.paper',
            transition: theme.transitions.create(['background-color'], {
              duration: theme.transitions.duration.standard,
            }),
          },
        }}
      >
        <Box
          role="presentation"
          sx={{
            pt: `${isMobile ? 56 : 64}px`,
          }}
        >
          <List>
            {menuItems.map((item) => (
              <ListItem 
                button 
                key={item.text}
                onClick={() => handleNavigation(item.path)}
                selected={location.pathname === item.path}
                sx={{
                  py: isMobile ? 1.5 : 2,
                  '&.Mui-selected': {
                    bgcolor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'inherit',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ color: location.pathname === item.path ? 'inherit' : 'primary.main' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: isMobile ? '0.9rem' : '1rem',
                    fontWeight: 500,
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          p: { xs: 1, sm: 2, md: 3 },
          mt: `${isMobile ? 56 : 64}px`,
          width: '100%',
          boxSizing: 'border-box',
          transition: theme.transitions.create(['padding'], {
            duration: theme.transitions.duration.standard,
          }),
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout; 