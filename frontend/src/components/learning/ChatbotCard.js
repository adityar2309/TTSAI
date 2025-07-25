import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Button,
  Avatar,
  Chip,
  Stack,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Chat as ChatIcon,
  ArrowForward as ArrowForwardIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

// Styled components
const StyledChatbotCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
}));

const ChatPreview = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.background.default,
  borderRadius: theme.shape.borderRadius,
  border: `1px solid ${theme.palette.divider}`,
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
}));

const ChatBubble = styled(Box)(({ theme, sender }) => ({
  backgroundColor: sender === 'avatar' ? theme.palette.primary.light : theme.palette.grey[100],
  color: sender === 'avatar' ? theme.palette.primary.contrastText : theme.palette.text.primary,
  borderRadius: sender === 'avatar' ? '16px 16px 16px 4px' : '16px 16px 4px 16px',
  padding: theme.spacing(1.5, 2),
  maxWidth: '80%',
  marginLeft: sender === 'avatar' ? 0 : 'auto',
  marginRight: sender === 'avatar' ? 'auto' : 0,
  marginBottom: theme.spacing(1),
  position: 'relative',
}));

/**
 * Chatbot card component for learning tools
 * 
 * @param {Object} props
 * @param {Object} props.avatar - Avatar information (name, image, role)
 * @param {Array} props.recentMessages - Recent messages to show in preview
 * @param {number} props.totalConversations - Total number of conversations
 * @param {string} props.lastTopic - Last conversation topic
 * @param {function} props.onStartChat - Callback when start chat button is clicked
 * @param {function} props.onChangeAvatar - Callback when change avatar button is clicked
 * @param {Object} props.sx - Additional styles
 */
const ChatbotCard = ({
  avatar = { name: 'AI Assistant', image: '🤖', role: 'Language Tutor' },
  recentMessages = [],
  totalConversations = 0,
  lastTopic = 'General Conversation',
  onStartChat,
  onChangeAvatar,
  sx = {},
  ...props
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Default messages if none provided
  const previewMessages = recentMessages.length > 0 ? recentMessages : [
    { sender: 'avatar', text: 'Hello! How can I help you practice today?' },
    { sender: 'user', text: 'I want to learn some new vocabulary.' },
  ];
  
  return (
    <StyledChatbotCard elevation={3} sx={sx} {...props}>
      <CardContent>
        {/* Card header with avatar info */}
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
          <Avatar
            sx={{
              bgcolor: 'primary.main',
              width: 56,
              height: 56,
              fontSize: '1.5rem',
            }}
          >
            {avatar.image || <PersonIcon />}
          </Avatar>
          
          <Box>
            <Typography variant="h6" component="h3">
              {avatar.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {avatar.role}
            </Typography>
          </Box>
        </Stack>
        
        {/* Chat statistics */}
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Conversations
            </Typography>
            <Typography variant="h6">
              {totalConversations}
            </Typography>
          </Box>
          
          <Divider orientation="vertical" flexItem />
          
          <Box sx={{ flex: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Last Topic
            </Typography>
            <Chip
              label={lastTopic}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>
        </Stack>
        
        {/* Chat preview */}
        <ChatPreview>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Recent Conversation
          </Typography>
          
          {previewMessages.map((message, index) => (
            <ChatBubble key={index} sender={message.sender}>
              <Typography variant="body2">
                {message.text}
              </Typography>
            </ChatBubble>
          ))}
        </ChatPreview>
        
        {/* Features */}
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Features
        </Typography>
        <Stack direction="row" spacing={1} sx={{ mb: 1, flexWrap: 'wrap', gap: 1 }}>
          <Chip label="Vocabulary Practice" size="small" />
          <Chip label="Grammar Correction" size="small" />
          <Chip label="Pronunciation Tips" size="small" />
        </Stack>
      </CardContent>
      
      <CardActions sx={{ p: 2, pt: 0, justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          onClick={onChangeAvatar}
          size={isMobile ? 'small' : 'medium'}
        >
          Change Avatar
        </Button>
        
        <Button
          variant="contained"
          color="primary"
          endIcon={<ArrowForwardIcon />}
          onClick={onStartChat}
          size={isMobile ? 'small' : 'medium'}
        >
          Start Chat
        </Button>
      </CardActions>
    </StyledChatbotCard>
  );
};

export default ChatbotCard;