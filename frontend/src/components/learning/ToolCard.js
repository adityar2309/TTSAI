import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Button,
  IconButton,
  Chip,
  useTheme,
  useMediaQuery,
  Divider,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { 
  ArrowForward as ArrowForwardIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

// Styled components
const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
  overflow: 'visible',
}));

const CardIconContainer = styled(Box)(({ theme, color = 'primary.main' }) => ({
  width: 56,
  height: 56,
  borderRadius: '50%',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  backgroundColor: color,
  color: theme.palette.getContrastText(theme.palette[color.split('.')[0]][color.split('.')[1]] || theme.palette.primary.main),
  fontSize: '1.5rem',
  marginBottom: theme.spacing(2),
  boxShadow: theme.shadows[2],
  [theme.breakpoints.down('sm')]: {
    width: 48,
    height: 48,
    fontSize: '1.25rem',
  },
}));

/**
 * Tool card component for learning tools
 * 
 * @param {Object} props
 * @param {string} props.title - Card title
 * @param {string} props.description - Card description
 * @param {React.ReactNode} props.icon - Icon component or emoji string
 * @param {string} props.iconColor - Color for icon background (default: 'primary.main')
 * @param {React.ReactNode} props.content - Main card content
 * @param {string} props.actionText - Text for action button (default: 'Open')
 * @param {function} props.onAction - Callback for action button
 * @param {string} props.status - Status text to display as chip
 * @param {string} props.statusColor - Color for status chip (default: 'default')
 * @param {boolean} props.featured - Whether card is featured (default: false)
 * @param {Object} props.sx - Additional styles
 */
const ToolCard = ({
  title,
  description,
  icon,
  iconColor = 'primary.main',
  content,
  actionText = 'Open',
  onAction,
  status,
  statusColor = 'default',
  featured = false,
  sx = {},
  ...props
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  return (
    <StyledCard
      elevation={featured ? 4 : 2}
      sx={{
        borderLeft: featured ? `4px solid ${theme.palette.primary.main}` : undefined,
        ...sx,
      }}
      {...props}
    >
      {/* Card header with icon and title */}
      <CardContent sx={{ pb: 1, flexGrow: 0 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {icon && (
              <CardIconContainer color={iconColor}>
                {typeof icon === 'string' ? icon : icon}
              </CardIconContainer>
            )}
            <Box sx={{ ml: icon ? 2 : 0 }}>
              <Typography variant="h6" component="h3" gutterBottom={!!description}>
                {title}
              </Typography>
              {description && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {description}
                </Typography>
              )}
            </Box>
          </Box>
          
          {status && (
            <Chip
              label={status}
              color={statusColor}
              size="small"
              sx={{ ml: 1 }}
            />
          )}
        </Box>
      </CardContent>
      
      {/* Divider if both content and actions exist */}
      {content && <Divider />}
      
      {/* Card content */}
      {content && (
        <CardContent sx={{ pt: 2, pb: 2, flexGrow: 1 }}>
          {content}
        </CardContent>
      )}
      
      {/* Card actions */}
      <CardActions sx={{ mt: 'auto', justifyContent: 'space-between', pt: 0 }}>
        <Box>
          <IconButton size="small" aria-label="info">
            <InfoIcon fontSize="small" />
          </IconButton>
        </Box>
        
        {onAction && (
          <Button
            size={isMobile ? 'small' : 'medium'}
            endIcon={<ArrowForwardIcon />}
            onClick={onAction}
          >
            {actionText}
          </Button>
        )}
      </CardActions>
    </StyledCard>
  );
};

export default ToolCard;