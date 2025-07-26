import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Divider,
  Alert,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import {
  School,
  Quiz,
  Chat,
  TrendingUp,
  Security,
  Speed
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import GoogleSignInButton from './GoogleSignInButton';

const LoginPage = () => {
  const { isAuthenticated, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/learning-tools';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  const handleSignInSuccess = (user) => {
    console.log('Sign in successful:', user);
    const from = location.state?.from?.pathname || '/learning-tools';
    navigate(from, { replace: true });
  };

  const handleSignInError = (error) => {
    console.error('Sign in error:', error);
  };

  const features = [
    {
      icon: <Quiz color="primary" />,
      title: 'Interactive Quizzes',
      description: 'Test your knowledge with personalized quizzes'
    },
    {
      icon: <Chat color="primary" />,
      title: 'AI Chatbot',
      description: 'Practice conversations with our AI language tutor'
    },
    {
      icon: <TrendingUp color="primary" />,
      title: 'Progress Tracking',
      description: 'Monitor your learning progress across all tools'
    },
    {
      icon: <School color="primary" />,
      title: 'Personalized Learning',
      description: 'Content adapted to your learning style and pace'
    },
    {
      icon: <Security color="primary" />,
      title: 'Secure & Private',
      description: 'Your data is protected with enterprise-grade security'
    },
    {
      icon: <Speed color="primary" />,
      title: 'Fast & Responsive',
      description: 'Optimized for the best learning experience'
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={4} alignItems="center" minHeight="80vh">
        {/* Left side - Features */}
        <Grid item xs={12} md={6}>
          <Box sx={{ pr: { md: 4 } }}>
            <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
              Welcome to Learning Tools
            </Typography>
            
            <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
              Enhance your language learning journey with personalized tools and AI-powered features
            </Typography>

            <Grid container spacing={3}>
              {features.map((feature, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Box sx={{ flexShrink: 0, mt: 0.5 }}>
                      {feature.icon}
                    </Box>
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
                        {feature.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {feature.description}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Grid>

        {/* Right side - Login form */}
        <Grid item xs={12} md={6}>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Paper
              elevation={8}
              sx={{
                p: 4,
                maxWidth: 400,
                width: '100%',
                borderRadius: 3
              }}
            >
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                  Sign In
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Access your personalized learning dashboard
                </Typography>
              </Box>

              {error && (
                <Alert 
                  severity="error" 
                  sx={{ mb: 3 }}
                  onClose={clearError}
                >
                  {error}
                </Alert>
              )}

              <GoogleSignInButton
                fullWidth
                size="large"
                text="Continue with Google"
                onSuccess={handleSignInSuccess}
                onError={handleSignInError}
              />

              <Divider sx={{ my: 3 }}>
                <Typography variant="caption" color="text.secondary">
                  Secure authentication
                </Typography>
              </Divider>

              <Card variant="outlined" sx={{ backgroundColor: 'grey.50' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center' }}>
                    By signing in, you agree to our{' '}
                    <Typography component="span" variant="caption" color="primary" sx={{ cursor: 'pointer' }}>
                      Terms of Service
                    </Typography>
                    {' '}and{' '}
                    <Typography component="span" variant="caption" color="primary" sx={{ cursor: 'pointer' }}>
                      Privacy Policy
                    </Typography>
                  </Typography>
                </CardContent>
              </Card>

              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  New to Learning Tools?{' '}
                  <Typography component="span" variant="body2" color="primary" sx={{ cursor: 'pointer', fontWeight: 500 }}>
                    Learn more about our features
                  </Typography>
                </Typography>
              </Box>
            </Paper>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default LoginPage;