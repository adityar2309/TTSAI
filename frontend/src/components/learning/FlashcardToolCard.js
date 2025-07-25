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
  Stack,
  IconButton,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  FlashOn as FlashOnIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';

// Styled components
const StyledFlashcardCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
}));

const FlashcardPreview = styled(Box)(({ theme }) => ({
  position: 'relative',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.default,
  borderRadius: theme.shape.borderRadius,
  border: `1px solid ${theme.palette.divider}`,
  minHeight: 80,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  margin: theme.spacing(0, 0, 2),
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: -8,
    left: 20,
    width: '70%',
    height: 8,
    backgroundColor: theme.palette.background.default,
    borderBottomLeftRadius: theme.shape.borderRadius,
    borderBottomRightRadius: theme.shape.borderRadius,
    border: `1px solid ${theme.palette.divider}`,
    borderTop: 'none',
    zIndex: -1,
  },
}));

/**
 * Flashcard tool card component for learning tools
 * 
 * @param {Object} props
 * @param {number} props.totalCards - Total number of flashcards
 * @param {number} props.dueCards - Number of cards due for review
 * @param {number} props.masteredCards - Number of mastered cards
 * @param {Array} props.previewCards - Array of preview cards to show
 * @param {function} props.onStartReview - Callback when start review button is clicked
 * @param {function} props.onCreateCard - Callback when create card button is clicked
 * @param {Object} props.sx - Additional styles
 */
const FlashcardToolCard = ({
  totalCards = 0,
  dueCards = 0,
  masteredCards = 0,
  previewCards = [],
  onStartReview,
  onCreateCard,
  sx = {},
  ...props
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Calculate mastery percentage
  const masteryPercentage = totalCards > 0 ? Math.round((masteredCards / totalCards) * 100) : 0;
  
  // Get a random preview card if available
  const previewCard = previewCards.length > 0 ? previewCards[0] : null;
  
  return (
    <StyledFlashcardCard elevation={3} sx={sx} {...props}>
      <CardContent>
        {/* Card header */}
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <Box
            sx={{
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              borderRadius: '50%',
              width: 40,
              height: 40,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <FlashOnIcon />
          </Box>
          <Typography variant="h6" component="h3">
            Flashcards
          </Typography>
        </Stack>
        
        {/* Flashcard stats */}
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Box sx={{ textAlign: 'center', flex: 1 }}>
            <Typography variant="h4" color="primary.main">
              {totalCards}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total
            </Typography>
          </Box>
          
          <Divider orientation="vertical" flexItem />
          
          <Box sx={{ textAlign: 'center', flex: 1 }}>
            <Typography variant="h4" color="warning.main">
              {dueCards}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Due
            </Typography>
          </Box>
          
          <Divider orientation="vertical" flexItem />
          
          <Box sx={{ textAlign: 'center', flex: 1 }}>
            <Typography variant="h4" color="success.main">
              {masteredCards}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Mastered
            </Typography>
          </Box>
        </Stack>
        
        {/* Mastery progress */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary">
              Mastery Progress
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {masteryPercentage}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={masteryPercentage}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
        
        {/* Flashcard preview */}
        {previewCard ? (
          <FlashcardPreview>
            <Typography variant="body1" align="center" fontWeight="medium">
              {previewCard.front || 'No cards available'}
            </Typography>
          </FlashcardPreview>
        ) : (
          <FlashcardPreview>
            <Typography variant="body2" color="text.secondary" align="center">
              {totalCards > 0 ? 'Loading cards...' : 'No cards available'}
            </Typography>
          </FlashcardPreview>
        )}
        
        {/* Due cards info */}
        {dueCards > 0 && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <ScheduleIcon color="warning" sx={{ mr: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {dueCards} {dueCards === 1 ? 'card' : 'cards'} due for review
            </Typography>
          </Box>
        )}
        
        {/* Mastered cards info */}
        {masteredCards > 0 && (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <CheckCircleIcon color="success" sx={{ mr: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {masteredCards} {masteredCards === 1 ? 'card' : 'cards'} mastered
            </Typography>
          </Box>
        )}
      </CardContent>
      
      <CardActions sx={{ p: 2, pt: 0, justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={onCreateCard}
          size={isMobile ? 'small' : 'medium'}
        >
          Add Card
        </Button>
        
        <Button
          variant="contained"
          color="primary"
          endIcon={<ArrowForwardIcon />}
          onClick={onStartReview}
          disabled={totalCards === 0}
          size={isMobile ? 'small' : 'medium'}
        >
          Start Review
        </Button>
      </CardActions>
    </StyledFlashcardCard>
  );
};

export default FlashcardToolCard;