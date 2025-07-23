import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Security,
  PersonalizationOutlined,
  History,
  CloudSync
} from '@mui/icons-material';
import GoogleSignInButton from '../components/auth/GoogleSignInButton';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/learning-tools');
    }
  }, [isAuthenticated, navigate]);

  const handleLoginSuccess = () => {
    navigate('/learning-tools');
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Welcome Back
        </Typography>
        
        <Typography variant="body1" paragraph align="center" color="text.secondary" sx={{ mb: 3 }}>
          Sign in to access your personalized learning experience
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
          <GoogleSignInButton onSuccess={handleLoginSuccess} />
        </Box>
        
        <Divider sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary">
            Benefits
          </Typography>
        </Divider>
        
        <List>
          <ListItem>
            <ListItemIcon>
              <PersonalizationOutlined color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Personalized Learning" 
              secondary="Get content tailored to your progress and preferences" 
            />
          </ListItem>
          
          <ListItem>
            <ListItemIcon>
              <History color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Progress Tracking" 
              secondary="Track your learning journey and achievements" 
            />
          </ListItem>
          
          <ListItem>
            <ListItemIcon>
              <CloudSync color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Sync Across Devices" 
              secondary="Access your learning data from any device" 
            />
          </ListItem>
          
          <ListItem>
            <ListItemIcon>
              <Security color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Secure Authentication" 
              secondary="Your data is protected with Google's secure authentication" 
            />
          </ListItem>
        </List>
      </Paper>
    </Container>
  );
};

export default LoginPage;