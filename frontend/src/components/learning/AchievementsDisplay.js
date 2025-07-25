import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  LinearProgress,
  Stack,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  EmojiEvents as TrophyIcon,
  Lock as LockIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

// Styled components
const AchievementCard = styled(Card)(({ theme, unlocked }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  opacity: unlocked ? 1 : 0.6,
  border: unlocked ? `2px solid ${theme.palette.primary.main}` : `1px solid ${theme.palette.divider}`,
  '&:hover': {
    transform: unlocked ? 'translateY(-4px)' : 'none',
    boxShadow: unlocked ? theme.shadows[8] : theme.shadows[2],
  },
}));

const AchievementIcon = styled(Box)(({ theme, unlocked }) => ({
  fontSize: '3rem',
  textAlign: 'center',
  marginBottom: theme.spacing(1),
  filter: unlocked ? 'none' : 'grayscale(100%)',
}));

const ProgressRing = styled(Box)(({ theme }) => ({
  position: 'relative',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 60,
  height: 60,
  marginBottom: theme.spacing(1),
}));

/**
 * Achievements display component
 * 
 * @param {Object} props
 * @param {Array} props.achievements - Array of achievement objects
 * @param {function} props.onAchievementClick - Callback when achievement is clicked
 * @param {boolean} props.showProgress - Whether to show progress for locked achievements
 * @param {string} props.layout - Layout type ('grid' or 'list')
 */
const AchievementsDisplay = ({
  achievements = [],
  onAchievementClick,
  showProgress = true,
  layout = 'grid',
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [selectedAchievement, setSelectedAchievement] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  
  // Default achievements if none provided
  const defaultAchievements = [
    {
      id: 'first-steps',
      name: 'First Steps',
      description: 'Complete your first lesson',
      icon: '👶',
      unlocked: true,
      unlockedAt: '2024-01-15',
      category: 'Getting Started',
      rarity: 'common',
      points: 10,
    },
    {
      id: 'week-warrior',
      name: 'Week Warrior',
      description: 'Maintain a 7-day learning streak',
      icon: '🔥',
      unlocked: true,
      unlockedAt: '2024-01-22',
      category: 'Consistency',
      rarity: 'uncommon',
      points: 25,
    },
    {
      id: 'quiz-master',
      name: 'Quiz Master',
      description: 'Complete 10 quizzes with 80% or higher',
      icon: '🏆',
      unlocked: false,
      progress: 7,
      target: 10,
      category: 'Mastery',
      rarity: 'rare',
      points: 50,
    },
    {
      id: 'vocabulary-expert',
      name: 'Vocabulary Expert',
      description: 'Learn 100 new words',
      icon: '📚',
      unlocked: false,
      progress: 65,
      target: 100,
      category: 'Learning',
      rarity: 'uncommon',
      points: 30,
    },
    {
      id: 'conversation-king',
      name: 'Conversation King',
      description: 'Have 50 conversations with AI avatars',
      icon: '👑',
      unlocked: false,
      progress: 12,
      target: 50,
      category: 'Practice',
      rarity: 'epic',
      points: 100,
    },
    {
      id: 'perfectionist',
      name: 'Perfectionist',
      description: 'Get 100% on 5 consecutive quizzes',
      icon: '💎',
      unlocked: false,
      progress: 2,
      target: 5,
      category: 'Excellence',
      rarity: 'legendary',
      points: 200,
    },
  ];
  
  // Use provided achievements or default achievements
  const displayAchievements = achievements.length > 0 ? achievements : defaultAchievements;
  
  // Handle achievement click
  const handleAchievementClick = (achievement) => {
    setSelectedAchievement(achievement);
    setDialogOpen(true);
    
    if (onAchievementClick) {
      onAchievementClick(achievement);
    }
  };
  
  // Handle dialog close
  const handleDialogClose = () => {
    setDialogOpen(false);
    setSelectedAchievement(null);
  };
  
  // Get rarity color
  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'common':
        return 'default';
      case 'uncommon':
        return 'primary';
      case 'rare':
        return 'secondary';
      case 'epic':
        return 'warning';
      case 'legendary':
        return 'error';
      default:
        return 'default';
    }
  };
  
  // Calculate progress percentage
  const getProgressPercentage = (achievement) => {
    if (!achievement.progress || !achievement.target) return 0;
    return Math.round((achievement.progress / achievement.target) * 100);
  };
  
  // Separate unlocked and locked achievements
  const unlockedAchievements = displayAchievements.filter(a => a.unlocked);
  const lockedAchievements = displayAchievements.filter(a => !a.unlocked);
  
  return (
    <Box>
      {/* Unlocked Achievements */}
      {unlockedAchievements.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <TrophyIcon sx={{ mr: 1 }} color="primary" />
            Unlocked Achievements ({unlockedAchievements.length})
          </Typography>
          
          <Grid container spacing={2}>
            {unlockedAchievements.map((achievement) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={achievement.id}>
                <AchievementCard
                  elevation={3}
                  unlocked={true}
                  onClick={() => handleAchievementClick(achievement)}
                >
                  <CardContent sx={{ textAlign: 'center', p: 2 }}>
                    <AchievementIcon unlocked={true}>
                      {achievement.icon}
                    </AchievementIcon>
                    
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {achievement.name}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {achievement.description}
                    </Typography>
                    
                    <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap">
                      <Chip
                        label={achievement.rarity}
                        size="small"
                        color={getRarityColor(achievement.rarity)}
                      />
                      <Chip
                        label={`${achievement.points} pts`}
                        size="small"
                        variant="outlined"
                      />
                    </Stack>
                  </CardContent>
                </AchievementCard>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      {/* Locked Achievements */}
      {lockedAchievements.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <LockIcon sx={{ mr: 1 }} color="action" />
            Locked Achievements ({lockedAchievements.length})
          </Typography>
          
          <Grid container spacing={2}>
            {lockedAchievements.map((achievement) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={achievement.id}>
                <AchievementCard
                  elevation={1}
                  unlocked={false}
                  onClick={() => handleAchievementClick(achievement)}
                >
                  <CardContent sx={{ textAlign: 'center', p: 2 }}>
                    <AchievementIcon unlocked={false}>
                      {achievement.icon}
                    </AchievementIcon>
                    
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {achievement.name}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {achievement.description}
                    </Typography>
                    
                    {showProgress && achievement.progress !== undefined && achievement.target && (
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            Progress
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {achievement.progress} / {achievement.target}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={getProgressPercentage(achievement)}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    )}
                    
                    <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap">
                      <Chip
                        label={achievement.rarity}
                        size="small"
                        color={getRarityColor(achievement.rarity)}
                        variant="outlined"
                      />
                      <Chip
                        label={`${achievement.points} pts`}
                        size="small"
                        variant="outlined"
                      />
                    </Stack>
                  </CardContent>
                </AchievementCard>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      {/* Achievement Detail Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleDialogClose}
        maxWidth="sm"
        fullWidth
      >
        {selectedAchievement && (
          <>
            <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
              <Box sx={{ fontSize: '4rem', mb: 1 }}>
                {selectedAchievement.icon}
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {selectedAchievement.name}
              </Typography>
              <Chip
                label={selectedAchievement.rarity}
                color={getRarityColor(selectedAchievement.rarity)}
                sx={{ mt: 1 }}
              />
            </DialogTitle>
            
            <DialogContent>
              <Typography variant="body1" paragraph>
                {selectedAchievement.description}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Category
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedAchievement.category}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Points
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {selectedAchievement.points}
                  </Typography>
                </Grid>
                {selectedAchievement.unlocked && selectedAchievement.unlockedAt && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Unlocked on
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {new Date(selectedAchievement.unlockedAt).toLocaleDateString()}
                    </Typography>
                  </Grid>
                )}
                {!selectedAchievement.unlocked && selectedAchievement.progress !== undefined && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Progress
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <LinearProgress
                        variant="determinate"
                        value={getProgressPercentage(selectedAchievement)}
                        sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="body2" fontWeight="medium">
                        {selectedAchievement.progress} / {selectedAchievement.target}
                      </Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            
            <DialogActions>
              <Button onClick={handleDialogClose}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default AchievementsDisplay;