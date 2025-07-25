import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Skeleton,
  useTheme,
  useMediaQuery,
  Paper,
} from '@mui/material';
import {
  School as SchoolIcon,
  FlashOn as FlashOnIcon,
  Quiz as QuizIcon,
  Chat as ChatIcon,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import ToolsContainer from '../components/learning/ToolsContainer';
import ResponsiveGrid from '../components/learning/ResponsiveGrid';
import LearningToolsLayout from '../components/learning/LearningToolsLayout';
import MobileResponsiveContainer from '../components/learning/MobileResponsiveContainer';
import UserProfile from '../components/auth/UserProfile';

// Import the original LearningTools component
// This will be refactored and integrated into the new design
import LearningTools from '../components/LearningTools';

const LearningToolsPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  
  // Simulate loading state
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Navigation items for the sidebar
  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'flashcards', label: 'Flashcards', icon: <FlashOnIcon /> },
    { id: 'quizzes', label: 'Quizzes', icon: <QuizIcon /> },
    { id: 'conversation', label: 'Conversation', icon: <ChatIcon /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon /> },
  ];
  
  // Sidebar content
  const sidebarContent = (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
        Learning Tools
      </Typography>
      
      <List component="nav" sx={{ width: '100%' }}>
        {navigationItems.map((item) => (
          <ListItem key={item.id} disablePadding>
            <ListItemButton
              selected={activeSection === item.id}
              onClick={() => setActiveSection(item.id)}
              sx={{
                borderRadius: 1,
                mb: 0.5,
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
        Language
      </Typography>
      
      <Paper variant="outlined" sx={{ p: 1, mb: 2 }}>
        <Typography variant="body1">English</Typography>
      </Paper>
      
      {!isMobile && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="body2" color="text.secondary" align="center">
            Need help?
          </Typography>
          <Typography variant="body2" color="primary" align="center">
            View Tutorial
          </Typography>
        </Box>
      )}
    </Box>
  );
  
  // Main content based on active section
  const renderMainContent = () => {
    if (loading) {
      return (
        <Box>
          <Skeleton variant="rectangular" height={200} sx={{ mb: 2, borderRadius: 1 }} />
          <ResponsiveGrid>
            {[1, 2, 3, 4].map((item) => (
              <Skeleton key={item} variant="rectangular" height={180} sx={{ borderRadius: 1 }} />
            ))}
          </ResponsiveGrid>
        </Box>
      );
    }
    
    // For now, we'll use the original LearningTools component
    // This will be replaced with new components as they are developed
    return (
      <Box>
        {/* User profile at the top */}
        <MobileResponsiveContainer sx={{ mb: 3 }}>
          <UserProfile />
        </MobileResponsiveContainer>
        
        {/* Original LearningTools component */}
        <LearningTools 
          userId={user?.id || 'guest'} 
          language="en" 
        />
      </Box>
    );
  };
  
  return (
    <ToolsContainer>
      <LearningToolsLayout
        sidebar={sidebarContent}
        main={renderMainContent()}
      />
    </ToolsContainer>
  );
};

export default LearningToolsPage;