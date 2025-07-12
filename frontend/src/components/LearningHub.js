import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Stack,
  Button,
  CircularProgress,
  LinearProgress,
  Chip,
  Alert,
  Snackbar,
  Container,
  IconButton
} from '@mui/material';
import {
  School as SchoolIcon,
  MenuBook as MenuBookIcon,
  FlashOn as FlashOnIcon,
  Quiz as QuizIcon,
  Chat as ChatIcon,
  TrendingUp as TrendingUpIcon,
  EmojiEvents as EmojiEventsIcon,
  Explore as ExploreIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import axios from 'axios';
import WordExplorer from './learning_modules/WordExplorer';
import FlashcardManager from './learning_modules/FlashcardManager';
import ProgressTracker from './learning_modules/ProgressTracker';
import '../styles/gradients.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const LearningHub = ({ userId, language }) => {
  // State management
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });
  const [progressSummary, setProgressSummary] = useState(null);
  const [activeModule, setActiveModule] = useState('dashboard');
  const [moduleProps, setModuleProps] = useState({});

  // Fetch progress summary on component mount and language change
  useEffect(() => {
    if (language && language.trim() !== '') {
      fetchProgressSummary();
    }
  }, [language, userId]);

  const fetchProgressSummary = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/progress/summary`, {
        params: { userId, language }
      });
      setProgressSummary(response.data);
    } catch (err) {
      console.error('Error fetching progress summary:', err);
      setError('Failed to load progress summary');
      showNotification('Failed to load progress data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const navigateToModule = (moduleName, props = {}) => {
    setActiveModule(moduleName);
    setModuleProps(props);
  };

  const handleBackToDashboard = () => {
    setActiveModule('dashboard');
    setModuleProps({});
  };

  // Learning modules configuration
  const learningModules = [
    {
      id: 'word-explorer',
      title: 'Word Explorer',
      icon: <ExploreIcon />,
      emoji: '🔍',
      description: 'Discover new words with detailed explanations, pronunciation, and cultural context',
      color: 'avatar-gradient-blue',
      buttonText: 'Explore Words'
    },
    {
      id: 'flashcards',
      title: 'Flashcard Manager',
      icon: <FlashOnIcon />,
      emoji: '⚡',
      description: 'Review and manage your flashcards with spaced repetition system',
      color: 'avatar-gradient-green',
      buttonText: 'Review Cards',
      comingSoon: false
    },
    {
      id: 'quizzes',
      title: 'Quiz Generator',
      icon: <QuizIcon />,
      emoji: '📝',
      description: 'Test your knowledge with adaptive quizzes tailored to your level',
      color: 'avatar-gradient-purple',
      buttonText: 'Take Quiz',
      comingSoon: true
    },
    {
      id: 'ai-conversation',
      title: 'AI Conversation',
      icon: <ChatIcon />,
      emoji: '🗣️',
      description: 'Practice conversations with AI language partners',
      color: 'avatar-gradient-orange',
      buttonText: 'Start Chat',
      comingSoon: true
    },
    {
      id: 'grammar',
      title: 'Grammar Companion',
      icon: <MenuBookIcon />,
      emoji: '📚',
      description: 'Interactive grammar lessons with explanations and practice',
      color: 'avatar-gradient-pink',
      buttonText: 'Learn Grammar',
      comingSoon: true
    },
    {
      id: 'progress',
      title: 'Progress Tracker',
      icon: <TrendingUpIcon />,
      emoji: '📊',
      description: 'Comprehensive analytics and achievement tracking',
      color: 'avatar-gradient-purple',
      buttonText: 'View Progress',
      comingSoon: false
    }
  ];

  // Calculate level progress
  const calculateLevelProgress = () => {
    if (!progressSummary?.total_xp) return 0;
    const currentLevelXP = progressSummary.total_xp % 1000;
    return (currentLevelXP / 1000) * 100;
  };

  // Render specific module
  if (activeModule !== 'dashboard') {
    return (
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Button
            startIcon={<CloseIcon />}
            onClick={handleBackToDashboard}
            variant="outlined"
            sx={{ mb: 2 }}
          >
            Back to Learning Hub
          </Button>
        </Box>
        
        {activeModule === 'word-explorer' && (
          <WordExplorer 
            userId={userId} 
            language={language}
            onNotification={showNotification}
            {...moduleProps}
          />
        )}
        
        {activeModule === 'flashcards' && (
          <FlashcardManager 
            userId={userId} 
            language={language}
            onNotification={showNotification}
            {...moduleProps}
          />
        )}
        
        {activeModule === 'progress' && (
          <ProgressTracker 
            userId={userId} 
            language={language}
            onNotification={showNotification}
            {...moduleProps}
          />
        )}
        
        {/* Other modules will be implemented in future phases */}
        {!['word-explorer', 'flashcards', 'progress'].includes(activeModule) && (
          <Card className="card-gradient shadow-modern rounded-modern">
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h5" gutterBottom>
                Coming Soon!
              </Typography>
              <Typography color="text.secondary">
                This module is currently under development and will be available in the next update.
              </Typography>
            </CardContent>
          </Card>
        )}

        {/* Notification Snackbar */}
        <Snackbar
          open={notification.open}
          autoHideDuration={4000}
          onClose={() => setNotification({ ...notification, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={() => setNotification({ ...notification, open: false })} 
            severity={notification.severity}
            variant="filled"
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Container>
    );
  }

  // Main dashboard view
  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Language check */}
      {(!language || language.trim() === '') ? (
        <Card className="card-gradient shadow-modern">
          <CardContent>
            <Box display="flex" flexDirection="column" alignItems="center" p={4}>
              <SchoolIcon className="text-gradient" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h5" className="text-gradient" gutterBottom>
                Select a Language to Start Learning
              </Typography>
              <Typography variant="body1" color="text.secondary" align="center">
                Please select a target language in the translator to access learning tools.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Box className="animate-fade-in">
          {/* Main Title */}
          <Typography variant="h3" className="text-gradient" align="center" gutterBottom sx={{ mb: 4 }}>
            Your Learning Journey
          </Typography>

          {/* Progress Overview Card */}
          {loading ? (
            <Card className="card-gradient shadow-modern rounded-modern" sx={{ mb: 4 }}>
              <CardContent sx={{ p: 4, textAlign: 'center' }}>
                <CircularProgress size={40} />
                <Typography variant="body1" sx={{ mt: 2 }}>Loading your progress...</Typography>
              </CardContent>
            </Card>
          ) : progressSummary ? (
            <Card className="card-gradient shadow-modern rounded-modern" sx={{ mb: 4 }}>
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h5" className="text-gradient" align="center" gutterBottom>
                  Overall Progress
                </Typography>
                
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" className="text-gradient" fontWeight="bold">
                        {progressSummary.total_xp || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Total XP</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" className="text-gradient" fontWeight="bold">
                        {progressSummary.current_streak || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Day Streak</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" className="text-gradient" fontWeight="bold">
                        {progressSummary.words_learned || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Words Learned</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" className="text-gradient" fontWeight="bold">
                        Level {progressSummary.level || 1}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">Current Level</Typography>
                    </Box>
                  </Grid>
                </Grid>
                
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Progress to Level {(progressSummary.level || 1) + 1}</Typography>
                    <Typography variant="body2">{progressSummary.total_xp || 0}/1000 XP</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={calculateLevelProgress()} 
                    className="progress-gradient"
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              </CardContent>
            </Card>
          ) : null}

          {/* Learning Modules Grid */}
          <Typography variant="h5" className="text-gradient" gutterBottom sx={{ mb: 3 }}>
            Learning Modules
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {learningModules.map((module) => (
              <Grid item xs={12} sm={6} md={4} key={module.id}>
                <Card 
                  className="card-gradient shadow-modern rounded-modern transition-modern" 
                  sx={{ 
                    height: '100%', 
                    '&:hover': { transform: 'translateY(-4px)' },
                    opacity: module.comingSoon ? 0.7 : 1
                  }}
                >
                  <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <Box 
                        className={`${module.color} rounded-modern`} 
                        sx={{ p: 1.5, color: 'white', fontSize: '1.5rem', display: 'flex', alignItems: 'center' }}
                      >
                        {module.emoji}
                      </Box>
                      <Typography variant="h6" fontWeight="600">
                        {module.title}
                      </Typography>
                      {module.comingSoon && (
                        <Chip label="Soon" size="small" color="primary" variant="outlined" />
                      )}
                    </Stack>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3, flexGrow: 1 }}>
                      {module.description}
                    </Typography>

                    <Button
                      className="button-gradient"
                      fullWidth
                      onClick={() => module.comingSoon ? null : navigateToModule(module.id)}
                      disabled={module.comingSoon}
                      sx={{ mt: 'auto' }}
                    >
                      {module.buttonText}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Quick Stats Section */}
          {progressSummary && (
            <Card className="card-gradient shadow-modern rounded-modern">
              <CardContent sx={{ p: 3 }}>
                <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
                  <EmojiEventsIcon className="text-gradient" />
                  <Typography variant="h6" fontWeight="600">Quick Stats</Typography>
                </Stack>
                
                <Grid container spacing={3}>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h5" className="text-gradient">
                        {progressSummary.flashcard_stats?.total || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Flashcards
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h5" className="text-gradient">
                        {progressSummary.quiz_stats?.completed || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Quizzes Completed
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h5" className="text-gradient">
                        {Math.round(progressSummary.flashcard_stats?.avg_success_rate * 100) || 0}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Success Rate
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h5" className="text-gradient">
                        {progressSummary.conversation_stats?.total || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Conversations
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}
        </Box>
      )}

      {/* Error Display */}
      {error && (
        <Alert 
          severity="error" 
          onClose={() => setError('')}
          sx={{ mt: 2 }}
        >
          {error}
        </Alert>
      )}

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setNotification({ ...notification, open: false })} 
          severity={notification.severity}
          variant="filled"
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default LearningHub;