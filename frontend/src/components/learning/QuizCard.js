import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  Stack,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Quiz as QuizIcon,
  Timer as TimerIcon,
  EmojiEvents as TrophyIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';

// Styled components
const StyledQuizCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  overflow: 'hidden',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
}));

const QuizCardHeader = styled(Box)(({ theme, difficulty }) => {
  // Define colors based on difficulty
  const difficultyColors = {
    beginner: theme.palette.success.main,
    intermediate: theme.palette.warning.main,
    advanced: theme.palette.error.main,
  };
  
  const color = difficultyColors[difficulty] || theme.palette.primary.main;
  
  return {
    backgroundColor: color,
    color: theme.palette.getContrastText(color),
    padding: theme.spacing(2),
    position: 'relative',
    overflow: 'hidden',
    '&::after': {
      content: '""',
      position: 'absolute',
      top: 0,
      right: 0,
      width: '30%',
      height: '100%',
      backgroundImage: `linear-gradient(to right, transparent, ${color}88)`,
    },
  };
});

/**
 * Quiz card component for learning tools
 * 
 * @param {Object} props
 * @param {string} props.title - Quiz title
 * @param {string} props.description - Quiz description
 * @param {string} props.difficulty - Quiz difficulty (beginner, intermediate, advanced)
 * @param {number} props.questionCount - Number of questions
 * @param {number} props.timeLimit - Time limit in minutes
 * @param {number} props.progress - Progress percentage (0-100)
 * @param {number} props.bestScore - Best score percentage (0-100)
 * @param {function} props.onStart - Callback when start button is clicked
 * @param {function} props.onContinue - Callback when continue button is clicked
 * @param {boolean} props.inProgress - Whether quiz is in progress
 * @param {Object} props.sx - Additional styles
 */
const QuizCard = ({
  title,
  description,
  difficulty = 'beginner',
  questionCount = 10,
  timeLimit,
  progress = 0,
  bestScore,
  onStart,
  onContinue,
  inProgress = false,
  sx = {},
  ...props
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Difficulty label and icon
  const difficultyInfo = {
    beginner: { label: 'Beginner', icon: '🌱' },
    intermediate: { label: 'Intermediate', icon: '🌿' },
    advanced: { label: 'Advanced', icon: '🌳' },
  };
  
  const difficultyLabel = difficultyInfo[difficulty]?.label || 'Beginner';
  const difficultyIcon = difficultyInfo[difficulty]?.icon || '🌱';
  
  return (
    <StyledQuizCard elevation={3} sx={sx} {...props}>
      {/* Card header with difficulty color */}
      <QuizCardHeader difficulty={difficulty}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 40, height: 40 }}>
            <QuizIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" component="h3" fontWeight="bold">
              {title}
            </Typography>
            <Stack direction="row" alignItems="center" spacing={1}>
              <Chip
                label={difficultyLabel}
                size="small"
                icon={<Typography sx={{ fontSize: '0.875rem', mr: -0.5 }}>{difficultyIcon}</Typography>}
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'inherit',
                  fontWeight: 'bold',
                }}
              />
              {timeLimit && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <TimerIcon fontSize="small" />
                  <Typography variant="body2">{timeLimit} min</Typography>
                </Box>
              )}
            </Stack>
          </Box>
        </Stack>
      </QuizCardHeader>
      
      {/* Card content */}
      <CardContent sx={{ flexGrow: 1, pt: 2 }}>
        {description && (
          <Typography variant="body2" color="text.secondary" paragraph>
            {description}
          </Typography>
        )}
        
        <Stack spacing={2}>
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Questions
            </Typography>
            <Typography variant="h6">
              {questionCount}
            </Typography>
          </Box>
          
          {bestScore !== undefined && (
            <Box>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
                <TrophyIcon fontSize="small" color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Best Score
                </Typography>
              </Stack>
              <Typography variant="h6" color="primary.main">
                {bestScore}%
              </Typography>
            </Box>
          )}
          
          {inProgress && (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Progress
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ flexGrow: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={progress}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {progress}%
                </Typography>
              </Box>
            </Box>
          )}
        </Stack>
      </CardContent>
      
      {/* Card actions */}
      <CardActions sx={{ p: 2, pt: 0 }}>
        {inProgress ? (
          <Button
            variant="contained"
            color="primary"
            fullWidth
            startIcon={<PlayIcon />}
            onClick={onContinue}
            size={isMobile ? 'small' : 'medium'}
          >
            Continue
          </Button>
        ) : (
          <Button
            variant="contained"
            color="primary"
            fullWidth
            startIcon={<PlayIcon />}
            onClick={onStart}
            size={isMobile ? 'small' : 'medium'}
          >
            Start Quiz
          </Button>
        )}
      </CardActions>
    </StyledQuizCard>
  );
};

export default QuizCard;