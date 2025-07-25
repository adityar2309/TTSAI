import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Stack,
  CircularProgress,
  LinearProgress,
  Chip,
  Alert,
  Snackbar,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  EmojiEvents as EmojiEventsIcon,
  TrendingUp as TrendingUpIcon,
  LocalFireDepartment as LocalFireDepartmentIcon,
  MilitaryTech as MilitaryTechIcon,
  School as SchoolIcon,
  Quiz as QuizIcon,
  Chat as ChatIcon,
  FlashOn as FlashOnIcon,
  Star as StarIcon,
  CalendarToday as CalendarTodayIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  GpsFixed as TargetIcon,
  ShowChart as ShowChartIcon
} from '@mui/icons-material';
import axios from 'axios';
import '../../styles/gradients.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const ProgressTracker = ({ userId, language, onNotification }) => {
  // State management
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });
  const [timeRange, setTimeRange] = useState('all');

  // Time range options
  const timeRangeOptions = [
    { value: 'week', label: 'Past Week' },
    { value: 'month', label: 'Past Month' },
    { value: 'all', label: 'All Time' }
  ];

  // Fetch progress data when component mounts or filters change
  useEffect(() => {
    if (userId && language) {
      fetchProgressData();
    }
  }, [userId, language, timeRange]);

  const showNotification = useCallback((message, severity = 'info') => {
    setNotification({ open: true, message, severity });
    if (onNotification) {
      onNotification(message, severity);
    }
  }, [onNotification]);

  const fetchProgressData = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.get(`${API_URL}/progress/comprehensive`, {
        params: { 
          userId, 
          language, 
          timeRange 
        }
      });
      
      setProgressData(response.data);
    } catch (err) {
      console.error('Error fetching progress data:', err);
      const errorMessage = err.response?.data?.error || 'Failed to fetch progress data';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Calculate level progress percentage
  const calculateLevelProgress = () => {
    if (!progressData?.total_xp) return 0;
    const currentLevelXP = progressData.total_xp % 1000;
    return (currentLevelXP / 1000) * 100;
  };

  // Get streak color based on length
  const getStreakColor = (streak) => {
    if (streak >= 30) return '#FF6B35'; // Fire red
    if (streak >= 14) return '#FF9500'; // Orange  
    if (streak >= 7) return '#FFD23F'; // Yellow
    if (streak >= 3) return '#4CAF50'; // Green
    return '#9E9E9E'; // Gray
  };

  // Get level color based on level
  const getLevelColor = (level) => {
    if (level >= 20) return '#9C27B0'; // Purple
    if (level >= 15) return '#E91E63'; // Pink
    if (level >= 10) return '#FF5722'; // Deep Orange
    if (level >= 5) return '#FF9800'; // Orange
    return '#4CAF50'; // Green
  };

  // Predefined achievements
  const achievements = [
    {
      id: 'first_translation',
      name: 'First Steps',
      description: 'Complete your first translation',
      icon: '🎯',
      unlocked: progressData?.total_xp > 0,
      category: 'milestone'
    },
    {
      id: 'week_streak',
      name: 'Week Warrior',
      description: 'Maintain a 7-day learning streak',
      icon: '🔥',
      unlocked: progressData?.current_streak >= 7,
      category: 'streak'
    },
    {
      id: 'month_streak',
      name: 'Monthly Master',
      description: 'Maintain a 30-day learning streak',
      icon: '💎',
      unlocked: progressData?.current_streak >= 30,
      category: 'streak'
    },
    {
      id: 'quiz_master',
      name: 'Quiz Master',
      description: 'Complete 10 quizzes',
      icon: '🏆',
      unlocked: progressData?.quiz_stats?.completed >= 10,
      category: 'quiz'
    },
    {
      id: 'conversation_expert',
      name: 'Conversation Expert',
      description: 'Complete 5 AI conversations',
      icon: '💬',
      unlocked: progressData?.conversation_stats?.total >= 5,
      category: 'conversation'
    },
    {
      id: 'flashcard_collector',
      name: 'Card Collector',
      description: 'Create 50 flashcards',
      icon: '⚡',
      unlocked: progressData?.flashcard_stats?.total >= 50,
      category: 'flashcard'
    },
    {
      id: 'word_master',
      name: 'Word Master',
      description: 'Master 25 words',
      icon: '📚',
      unlocked: progressData?.words_learned >= 25,
      category: 'vocabulary'
    },
    {
      id: 'level_up',
      name: 'Level Up',
      description: 'Reach level 5',
      icon: '⭐',
      unlocked: progressData?.level >= 5,
      category: 'level'
    },
    {
      id: 'perfectionist',
      name: 'Perfectionist',
      description: 'Achieve 90% quiz success rate',
      icon: '🎖️',
      unlocked: progressData?.quiz_stats?.avg_score >= 90,
      category: 'performance'
    },
    {
      id: 'dedicated_learner',
      name: 'Dedicated Learner',
      description: 'Earn 1000 XP',
      icon: '🌟',
      unlocked: progressData?.total_xp >= 1000,
      category: 'xp'
    }
  ];

  const unlockedAchievements = achievements.filter(a => a.unlocked);
  const lockedAchievements = achievements.filter(a => !a.unlocked);

  if (loading) {
    return (
      <Box sx={{ maxWidth: '1000px', mx: 'auto' }}>
        <Card className="card-gradient shadow-modern rounded-modern">
          <CardContent sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress size={60} />
            <Typography variant="h6" sx={{ mt: 2 }}>
              Loading your progress...
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto' }}>
      {/* Main Card */}
      <Card className="card-gradient shadow-modern rounded-modern">
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Typography variant="h4" className="text-gradient" align="center" gutterBottom>
            Progress Tracker
          </Typography>
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
            Comprehensive analytics and achievement tracking for your learning journey
          </Typography>

          {/* Time Range Selector */}
          <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Time Range</InputLabel>
              <Select
                value={timeRange}
                label="Time Range"
                onChange={(e) => setTimeRange(e.target.value)}
              >
                {timeRangeOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {progressData ? (
            <Box>
              {/* Key Metrics Overview */}
              <Typography variant="h5" className="text-gradient" gutterBottom sx={{ mb: 3 }}>
                Key Metrics Overview
              </Typography>
              
              <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Total XP */}
                <Grid item xs={6} md={3}>
                  <Paper elevation={2} sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                    <Avatar 
                      className="avatar-gradient-blue"
                      sx={{ width: 56, height: 56, mx: 'auto', mb: 2 }}
                    >
                      <StarIcon fontSize="large" />
                    </Avatar>
                    <Typography variant="h4" className="text-gradient" fontWeight="bold">
                      {progressData.total_xp?.toLocaleString() || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total XP
                    </Typography>
                  </Paper>
                </Grid>

                {/* Current Streak */}
                <Grid item xs={6} md={3}>
                  <Paper elevation={2} sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                    <Avatar 
                      sx={{ 
                        width: 56, 
                        height: 56, 
                        mx: 'auto', 
                        mb: 2,
                        bgcolor: getStreakColor(progressData.current_streak)
                      }}
                    >
                      <LocalFireDepartmentIcon fontSize="large" />
                    </Avatar>
                    <Typography variant="h4" className="text-gradient" fontWeight="bold">
                      {progressData.current_streak || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Day Streak
                    </Typography>
                  </Paper>
                </Grid>

                {/* Words Learned */}
                <Grid item xs={6} md={3}>
                  <Paper elevation={2} sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                    <Avatar 
                      className="avatar-gradient-green"
                      sx={{ width: 56, height: 56, mx: 'auto', mb: 2 }}
                    >
                      <SchoolIcon fontSize="large" />
                    </Avatar>
                    <Typography variant="h4" className="text-gradient" fontWeight="bold">
                      {progressData.words_learned || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Words Learned
                    </Typography>
                  </Paper>
                </Grid>

                {/* Current Level */}
                <Grid item xs={6} md={3}>
                  <Paper elevation={2} sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                    <Avatar 
                      sx={{ 
                        width: 56, 
                        height: 56, 
                        mx: 'auto', 
                        mb: 2,
                        bgcolor: getLevelColor(progressData.level)
                      }}
                    >
                      <MilitaryTechIcon fontSize="large" />
                    </Avatar>
                    <Typography variant="h4" className="text-gradient" fontWeight="bold">
                      {progressData.level || 1}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Current Level
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Level Progress */}
              <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Progress to Level {(progressData.level || 1) + 1}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={calculateLevelProgress()} 
                      className="progress-gradient"
                      sx={{ height: 12, borderRadius: 6 }}
                    />
                  </Box>
                  <Box sx={{ minWidth: 35 }}>
                    <Typography variant="body2" color="text.secondary">
                      {Math.round(calculateLevelProgress())}%
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {progressData.total_xp % 1000} / 1000 XP to next level
                </Typography>
              </Paper>

              {/* Performance Stats Grid */}
              <Grid container spacing={3} sx={{ mb: 4 }}>
                {/* Flashcard Performance */}
                <Grid item xs={12} md={4}>
                  <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <FlashOnIcon className="text-gradient" fontSize="large" />
                      <Typography variant="h6" fontWeight="600">
                        Flashcard Performance
                      </Typography>
                    </Stack>
                    
                    <Stack spacing={2}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Total Cards:</Typography>
                        <Typography variant="body2" fontWeight="600">
                          {progressData.flashcard_stats?.total || 0}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Due for Review:</Typography>
                        <Chip 
                          label={progressData.flashcard_stats?.due_for_review || 0}
                          size="small"
                          color={progressData.flashcard_stats?.due_for_review > 0 ? 'warning' : 'default'}
                        />
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Mastered:</Typography>
                        <Typography variant="body2" fontWeight="600" color="success.main">
                          {progressData.flashcard_stats?.mastered || 0}
                        </Typography>
                      </Box>
                      
                      <Divider />
                      
                      <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2">Success Rate:</Typography>
                          <Typography variant="body2" fontWeight="600">
                            {Math.round((progressData.flashcard_stats?.avg_success_rate || 0) * 100)}%
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={(progressData.flashcard_stats?.avg_success_rate || 0) * 100} 
                          className="progress-gradient"
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    </Stack>
                  </Paper>
                </Grid>

                {/* Quiz Performance */}
                <Grid item xs={12} md={4}>
                  <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <QuizIcon className="text-gradient" fontSize="large" />
                      <Typography variant="h6" fontWeight="600">
                        Quiz Performance
                      </Typography>
                    </Stack>
                    
                    <Stack spacing={2}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Completed:</Typography>
                        <Typography variant="body2" fontWeight="600">
                          {progressData.quiz_stats?.completed || 0}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Average Score:</Typography>
                        <Chip 
                          label={`${Math.round(progressData.quiz_stats?.avg_score || 0)}%`}
                          size="small"
                          color={progressData.quiz_stats?.avg_score >= 80 ? 'success' : 
                                 progressData.quiz_stats?.avg_score >= 60 ? 'warning' : 'error'}
                        />
                      </Box>
                      
                      <Divider />
                      
                      <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2">Performance:</Typography>
                          <Typography variant="body2" fontWeight="600">
                            {progressData.quiz_stats?.avg_score >= 90 ? 'Excellent' :
                             progressData.quiz_stats?.avg_score >= 80 ? 'Good' :
                             progressData.quiz_stats?.avg_score >= 60 ? 'Fair' : 'Needs Improvement'}
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={progressData.quiz_stats?.avg_score || 0} 
                          className="progress-gradient"
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    </Stack>
                  </Paper>
                </Grid>

                {/* Conversation Stats */}
                <Grid item xs={12} md={4}>
                  <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <ChatIcon className="text-gradient" fontSize="large" />
                      <Typography variant="h6" fontWeight="600">
                        Conversation Stats
                      </Typography>
                    </Stack>
                    
                    <Stack spacing={2}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Total Sessions:</Typography>
                        <Typography variant="body2" fontWeight="600">
                          {progressData.conversation_stats?.total || 0}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">Avg Duration:</Typography>
                        <Typography variant="body2" fontWeight="600">
                          {Math.round(progressData.conversation_stats?.avg_duration / 60) || 0} min
                        </Typography>
                      </Box>
                      
                      {progressData.conversation_stats?.last_topic && (
                        <Box>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Last Topic:
                          </Typography>
                          <Chip 
                            label={progressData.conversation_stats.last_topic}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      )}
                    </Stack>
                  </Paper>
                </Grid>
              </Grid>

              {/* Activity Graph Placeholder */}
              <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
                <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                  <ShowChartIcon className="text-gradient" fontSize="large" />
                  <Typography variant="h6" fontWeight="600">
                    Activity Graph
                  </Typography>
                </Stack>
                
                <Alert severity="info" sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom>
                    📊 Activity Visualization Coming Soon
                  </Typography>
                  <Typography variant="body2">
                    We're working on interactive charts to visualize your daily activity, 
                    score trends, and learning patterns over time.
                  </Typography>
                </Alert>
                
                {/* Placeholder metrics */}
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h6" className="text-gradient">
                        {Math.round(progressData.total_xp / 30) || 0}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Avg XP/Day
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h6" className="text-gradient">
                        {timeRange === 'week' ? '7' : timeRange === 'month' ? '30' : '∞'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Days Tracked
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h6" className="text-gradient">
                        {Math.round(progressData.quiz_stats?.avg_score || 0)}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Best Score
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h6" className="text-gradient">
                        {progressData.current_streak || 0}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Best Streak
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>

              {/* Achievements Section */}
              <Typography variant="h5" className="text-gradient" gutterBottom sx={{ mb: 3 }}>
                Achievements & Badges
              </Typography>
              
              <Grid container spacing={3}>
                {/* Unlocked Achievements */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={2} sx={{ p: 3 }}>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <EmojiEventsIcon className="text-gradient" />
                      <Typography variant="h6" fontWeight="600">
                        Unlocked ({unlockedAchievements.length})
                      </Typography>
                    </Stack>
                    
                    <List dense>
                      {unlockedAchievements.map((achievement) => (
                        <ListItem key={achievement.id} sx={{ px: 0 }}>
                          <ListItemIcon>
                            <Typography variant="h5">{achievement.icon}</Typography>
                          </ListItemIcon>
                          <ListItemText
                            primary={achievement.name}
                            secondary={achievement.description}
                            primaryTypographyProps={{ fontWeight: 600 }}
                          />
                          <Chip 
                            label="Unlocked" 
                            size="small" 
                            color="success" 
                            variant="outlined"
                          />
                        </ListItem>
                      ))}
                      
                      {unlockedAchievements.length === 0 && (
                        <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                          No achievements unlocked yet. Keep learning to earn your first badge!
                        </Typography>
                      )}
                    </List>
                  </Paper>
                </Grid>

                {/* Locked Achievements */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={2} sx={{ p: 3 }}>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <TargetIcon className="text-gradient" />
                      <Typography variant="h6" fontWeight="600">
                        Goals ({lockedAchievements.length})
                      </Typography>
                    </Stack>
                    
                    <List dense>
                      {lockedAchievements.slice(0, 5).map((achievement) => (
                        <ListItem key={achievement.id} sx={{ px: 0, opacity: 0.6 }}>
                          <ListItemIcon>
                            <Typography variant="h5" sx={{ filter: 'grayscale(100%)' }}>
                              {achievement.icon}
                            </Typography>
                          </ListItemIcon>
                          <ListItemText
                            primary={achievement.name}
                            secondary={achievement.description}
                            primaryTypographyProps={{ fontWeight: 600 }}
                          />
                          <Chip 
                            label="Locked" 
                            size="small" 
                            variant="outlined"
                          />
                        </ListItem>
                      ))}
                      
                      {lockedAchievements.length > 5 && (
                        <Typography variant="caption" color="text.secondary" textAlign="center" display="block" mt={1}>
                          +{lockedAchievements.length - 5} more achievements to unlock
                        </Typography>
                      )}
                    </List>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          ) : (
            <Alert severity="info" sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                📈 Start Your Learning Journey
              </Typography>
              <Typography variant="body2">
                Complete some translations, flashcard reviews, or quizzes to see your progress here!
              </Typography>
            </Alert>
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
        </CardContent>
      </Card>

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
    </Box>
  );
};

export default ProgressTracker;