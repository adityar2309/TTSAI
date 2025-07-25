import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Grid,
  Divider,
  Stack,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';

// Styled components
const StatCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const StatHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginBottom: theme.spacing(2),
}));

const StatValue = styled(Typography)(({ theme }) => ({
  fontSize: '2rem',
  fontWeight: 'bold',
  color: theme.palette.primary.main,
}));

const ProgressContainer = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(2),
}));

/**
 * Detailed statistics component for learning progress
 * 
 * @param {Object} props
 * @param {Object} props.stats - Statistics data
 * @param {Array} props.recentActivity - Recent activity data
 * @param {Object} props.weeklyProgress - Weekly progress data
 * @param {Array} props.skillLevels - Skill level data
 */
const DetailedStats = ({
  stats = {},
  recentActivity = [],
  weeklyProgress = {},
  skillLevels = [],
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Default stats
  const defaultStats = {
    totalStudyTime: 0, // in minutes
    averageSessionTime: 0, // in minutes
    accuracyRate: 0, // percentage
    improvementRate: 0, // percentage
    ...stats,
  };
  
  // Default weekly progress
  const defaultWeeklyProgress = {
    currentWeek: 0,
    lastWeek: 0,
    target: 100,
    ...weeklyProgress,
  };
  
  // Default skill levels
  const defaultSkillLevels = [
    { skill: 'Vocabulary', level: 65, target: 80 },
    { skill: 'Grammar', level: 45, target: 70 },
    { skill: 'Listening', level: 55, target: 75 },
    { skill: 'Speaking', level: 40, target: 65 },
    { skill: 'Reading', level: 70, target: 85 },
    { skill: 'Writing', level: 35, target: 60 },
  ];
  
  // Use provided data or defaults
  const displaySkillLevels = skillLevels.length > 0 ? skillLevels : defaultSkillLevels;
  
  // Format time
  const formatTime = (minutes) => {
    if (minutes < 60) {
      return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };
  
  // Calculate weekly progress percentage
  const weeklyProgressPercentage = Math.round(
    (defaultWeeklyProgress.currentWeek / defaultWeeklyProgress.target) * 100
  );
  
  // Calculate improvement
  const weeklyImprovement = defaultWeeklyProgress.currentWeek - defaultWeeklyProgress.lastWeek;
  const improvementPercentage = defaultWeeklyProgress.lastWeek > 0 
    ? Math.round((weeklyImprovement / defaultWeeklyProgress.lastWeek) * 100)
    : 0;
  
  return (
    <Grid container spacing={3}>
      {/* Study Time Stats */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard elevation={2}>
          <CardContent>
            <StatHeader>
              <ScheduleIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Study Time</Typography>
            </StatHeader>
            
            <StatValue>
              {formatTime(defaultStats.totalStudyTime)}
            </StatValue>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Total this month
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="body2" color="text.secondary">
              Average session: {formatTime(defaultStats.averageSessionTime)}
            </Typography>
          </CardContent>
        </StatCard>
      </Grid>
      
      {/* Accuracy Stats */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard elevation={2}>
          <CardContent>
            <StatHeader>
              <AssessmentIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Accuracy</Typography>
            </StatHeader>
            
            <StatValue>
              {defaultStats.accuracyRate}%
            </StatValue>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Overall accuracy
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            <Stack direction="row" alignItems="center" spacing={1}>
              <TrendingUpIcon 
                fontSize="small" 
                color={defaultStats.improvementRate >= 0 ? 'success' : 'error'} 
              />
              <Typography 
                variant="body2" 
                color={defaultStats.improvementRate >= 0 ? 'success.main' : 'error.main'}
              >
                {defaultStats.improvementRate >= 0 ? '+' : ''}{defaultStats.improvementRate}% this week
              </Typography>
            </Stack>
          </CardContent>
        </StatCard>
      </Grid>
      
      {/* Weekly Progress */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard elevation={2}>
          <CardContent>
            <StatHeader>
              <SpeedIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Weekly Goal</Typography>
            </StatHeader>
            
            <StatValue>
              {defaultWeeklyProgress.currentWeek}
            </StatValue>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              of {defaultWeeklyProgress.target} XP target
            </Typography>
            
            <ProgressContainer>
              <LinearProgress
                variant="determinate"
                value={Math.min(weeklyProgressPercentage, 100)}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </ProgressContainer>
            
            <Typography variant="body2" color="text.secondary">
              {weeklyProgressPercentage}% complete
            </Typography>
          </CardContent>
        </StatCard>
      </Grid>
      
      {/* Improvement Rate */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard elevation={2}>
          <CardContent>
            <StatHeader>
              <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Improvement</Typography>
            </StatHeader>
            
            <StatValue color={improvementPercentage >= 0 ? 'success.main' : 'error.main'}>
              {improvementPercentage >= 0 ? '+' : ''}{improvementPercentage}%
            </StatValue>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              vs last week
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            <Chip
              label={improvementPercentage >= 0 ? 'Improving' : 'Needs Focus'}
              color={improvementPercentage >= 0 ? 'success' : 'warning'}
              size="small"
            />
          </CardContent>
        </StatCard>
      </Grid>
      
      {/* Skill Levels */}
      <Grid item xs={12}>
        <StatCard elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Skill Progress
            </Typography>
            
            <Grid container spacing={3}>
              {displaySkillLevels.map((skill, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body1" fontWeight="medium">
                        {skill.skill}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {skill.level}% / {skill.target}%
                      </Typography>
                    </Box>
                    
                    <LinearProgress
                      variant="determinate"
                      value={skill.level}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'grey.200',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: skill.level >= skill.target ? 'success.main' : 'primary.main',
                        },
                      }}
                    />
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        {skill.level >= skill.target ? 'Target reached!' : `${skill.target - skill.level}% to target`}
                      </Typography>
                      {skill.level >= skill.target && (
                        <Chip label="✓" size="small" color="success" />
                      )}
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </StatCard>
      </Grid>
    </Grid>
  );
};

export default DetailedStats;