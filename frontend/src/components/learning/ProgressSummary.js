import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Grid,
  Avatar,
  Chip,
  Stack,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  TrendingUp as TrendingUpIcon,
  EmojiEvents as TrophyIcon,
  LocalFire as FireIcon,
  School as SchoolIcon,
  Star as StarIcon,
} from '@mui/icons-material';

// Styled components
const StyledProgressCard = styled(Card)(({ theme }) => ({
  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
  color: theme.palette.primary.contrastText,
  marginBottom: theme.spacing(3),
}));

const StatCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  },
}));

const StatIcon = styled(Avatar)(({ theme, color = 'primary' }) => ({
  backgroundColor: theme.palette[color].main,
  color: theme.palette[color].contrastText,
  width: 48,
  height: 48,
  marginBottom: theme.spacing(1),
}));

const ProgressBar = styled(LinearProgress)(({ theme }) => ({
  height: 8,
  borderRadius: 4,
  backgroundColor: 'rgba(255, 255, 255, 0.2)',
  '& .MuiLinearProgress-bar': {
    borderRadius: 4,
    backgroundColor: theme.palette.primary.contrastText,
  },
}));

/**
 * Progress summary component for learning tools
 * 
 * @param {Object} props
 * @param {Object} props.user - User information
 * @param {Object} props.progress - Progress data
 * @param {Array} props.achievements - Array of achievement objects
 * @param {Array} props.stats - Array of stat objects
 * @param {boolean} props.showAchievements - Whether to show achievements section
 * @param {boolean} props.showStats - Whether to show stats section
 */
const ProgressSummary = ({
  user = null,
  progress = {},
  achievements = [],
  stats = [],
  showAchievements = true,
  showStats = true,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Default progress data
  const defaultProgress = {
    level: 1,
    xp: 0,
    xpToNext: 100,
    streak: 0,
    wordsLearned: 0,
    quizzesCompleted: 0,
    conversationMinutes: 0,
    ...progress,
  };
  
  // Default stats if none provided
  const defaultStats = [
    {
      id: 'level',
      label: 'Level',
      value: defaultProgress.level,
      icon: <SchoolIcon />,
      color: 'primary',
    },
    {
      id: 'streak',
      label: 'Day Streak',
      value: defaultProgress.streak,
      icon: <FireIcon />,
      color: 'warning',
    },
    {
      id: 'words',
      label: 'Words Learned',
      value: defaultProgress.wordsLearned,
      icon: <StarIcon />,
      color: 'success',
    },
    {
      id: 'quizzes',
      label: 'Quizzes Completed',
      value: defaultProgress.quizzesCompleted,
      icon: <TrophyIcon />,
      color: 'info',
    },
  ];
  
  // Use provided stats or default stats
  const displayStats = stats.length > 0 ? stats : defaultStats;
  
  // Default achievements if none provided
  const defaultAchievements = [
    { id: 'first-quiz', name: 'First Quiz', unlocked: true, icon: '🎯' },
    { id: 'week-streak', name: 'Week Streak', unlocked: defaultProgress.streak >= 7, icon: '🔥' },
    { id: 'quiz-master', name: 'Quiz Master', unlocked: defaultProgress.quizzesCompleted >= 10, icon: '🏆' },
    { id: 'vocabulary-expert', name: 'Vocabulary Expert', unlocked: defaultProgress.wordsLearned >= 100, icon: '📚' },
  ];
  
  // Use provided achievements or default achievements
  const displayAchievements = achievements.length > 0 ? achievements : defaultAchievements;
  
  // Calculate progress percentage
  const progressPercentage = Math.round((defaultProgress.xp / defaultProgress.xpToNext) * 100);
  
  return (
    <Box>
      {/* Main progress card */}
      <StyledProgressCard elevation={3}>
        <CardContent sx={{ p: isMobile ? 2 : 3 }}>
          <Grid container spacing={3} alignItems="center">
            {/* User info */}
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {user?.profilePicture ? (
                  <Avatar
                    src={user.profilePicture}
                    alt={user.name}
                    sx={{ width: 64, height: 64, mr: 2 }}
                  />
                ) : (
                  <Avatar sx={{ width: 64, height: 64, mr: 2, bgcolor: 'rgba(255,255,255,0.2)' }}>
                    <SchoolIcon fontSize="large" />
                  </Avatar>
                )}
                <Box>
                  <Typography variant="h6" fontWeight="bold">
                    {user?.name || 'Guest User'}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Level {defaultProgress.level} Learner
                  </Typography>
                </Box>
              </Box>
            </Grid>
            
            {/* Progress info */}
            <Grid item xs={12} sm={6} md={8}>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body1" fontWeight="medium">
                    Progress to Level {defaultProgress.level + 1}
                  </Typography>
                  <Typography variant="body2">
                    {defaultProgress.xp} / {defaultProgress.xpToNext} XP
                  </Typography>
                </Box>
                <ProgressBar
                  variant="determinate"
                  value={progressPercentage}
                  sx={{ mb: 2 }}
                />
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="h4" fontWeight="bold">
                      {defaultProgress.xp}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Total XP
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="h4" fontWeight="bold">
                      {defaultProgress.streak}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Day Streak
                    </Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="h4" fontWeight="bold">
                      {progressPercentage}%
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      To Next Level
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </StyledProgressCard>
      
      {/* Stats cards */}
      {showStats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {displayStats.map((stat) => (
            <Grid item xs={6} sm={3} key={stat.id}>
              <StatCard elevation={2}>
                <CardContent sx={{ textAlign: 'center', p: isMobile ? 1.5 : 2 }}>
                  <StatIcon color={stat.color}>
                    {stat.icon}
                  </StatIcon>
                  <Typography variant="h5" fontWeight="bold" gutterBottom>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </CardContent>
              </StatCard>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Achievements */}
      {showAchievements && displayAchievements.length > 0 && (
        <Card elevation={2}>
          <CardContent sx={{ p: isMobile ? 2 : 3 }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <TrophyIcon color="primary" />
              <Typography variant="h6" fontWeight="600">
                Achievements
              </Typography>
            </Stack>
            
            <Grid container spacing={2}>
              {displayAchievements.map((achievement) => (
                <Grid item xs={6} sm={4} md={3} key={achievement.id}>
                  <Box
                    sx={{
                      p: 2,
                      textAlign: 'center',
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: achievement.unlocked ? 'primary.main' : 'divider',
                      backgroundColor: achievement.unlocked ? 'primary.light' : 'background.default',
                      opacity: achievement.unlocked ? 1 : 0.6,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: achievement.unlocked ? 'scale(1.05)' : 'none',
                      },
                    }}
                  >
                    <Typography variant="h4" sx={{ mb: 1 }}>
                      {achievement.icon}
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="600"
                      color={achievement.unlocked ? 'primary.main' : 'text.secondary'}
                    >
                      {achievement.name}
                    </Typography>
                    {achievement.unlocked && (
                      <Chip
                        label="Unlocked"
                        size="small"
                        color="success"
                        sx={{ mt: 1 }}
                      />
                    )}
                  </Box>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ProgressSummary;