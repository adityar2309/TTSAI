import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemText,
  useTheme,
  useMediaQuery,
  Divider,
  Stack,
} from '@mui/material';
import {
  School,
  Chat,
  Public,
  Book,
  Psychology,
  Lightbulb,
} from '@mui/icons-material';

/**
 * LanguageTutor Component
 * 
 * Displays structured explanations from the RAG-powered language tutor.
 * Shows meaning, examples, grammar tips, and cultural insights in an organized format.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.explanation - The explanation object from the API
 * @param {string} props.explanation.meaning - Detailed meaning and nuances
 * @param {Array} props.explanation.examples - Array of example objects with sentence and translation
 * @param {string} props.explanation.grammar_tip - Grammar explanation
 * @param {string} props.explanation.cultural_insight - Cultural context and notes
 */
const LanguageTutor = ({ explanation }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Don't render if no explanation provided
  if (!explanation) {
    return null;
  }

  return (
    <Paper 
      elevation={2} 
      sx={{ 
        p: 3, 
        mt: 3, 
        bgcolor: 'background.default',
        borderRadius: 2,
        border: `1px solid ${theme.palette.divider}`,
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <School 
          color="primary" 
          sx={{ 
            mr: 1.5, 
            fontSize: isMobile ? '1.5rem' : '1.75rem' 
          }} 
        />
        <Typography 
          variant={isMobile ? "h6" : "h5"} 
          component="h3" 
          fontWeight="600"
          color="primary"
        >
          Language Tutor
        </Typography>
      </Box>

      <Stack spacing={3}>
        {/* Meaning & Nuances Section */}
        {explanation.meaning && (
          <Box>
            <Chip 
              icon={<Book />} 
              label="Meaning & Nuances" 
              color="primary" 
              variant="outlined"
              sx={{ 
                mb: 2, 
                fontWeight: 600,
                '& .MuiChip-icon': {
                  fontSize: '1.1rem'
                }
              }} 
            />
            <Typography 
              variant="body1" 
              sx={{ 
                pl: 1, 
                lineHeight: 1.7,
                color: 'text.primary'
              }}
            >
              {explanation.meaning}
            </Typography>
          </Box>
        )}

        {/* Example Sentences Section */}
        {explanation.examples && explanation.examples.length > 0 && (
          <Box>
            <Chip 
              icon={<Chat />} 
              label="Example Sentences" 
              color="secondary" 
              variant="outlined"
              sx={{ 
                mb: 2, 
                fontWeight: 600,
                '& .MuiChip-icon': {
                  fontSize: '1.1rem'
                }
              }} 
            />
            <List dense sx={{ pl: 1 }}>
              {explanation.examples.map((example, index) => (
                <ListItem 
                  key={index} 
                  sx={{ 
                    display: 'block', 
                    py: 1,
                    px: 0,
                    '&:not(:last-child)': {
                      borderBottom: `1px solid ${theme.palette.divider}`,
                      mb: 1,
                      pb: 2
                    }
                  }}
                >
                  {/* Example sentence */}
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      fontWeight: 500,
                      color: 'text.primary',
                      mb: 0.5
                    }}
                  >
                    "{typeof example === 'string' ? example : example.sentence}"
                  </Typography>
                  
                  {/* Translation */}
                  {typeof example === 'object' && example.translation && (
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ 
                        pl: 2, 
                        fontStyle: 'italic',
                        position: 'relative',
                        '&::before': {
                          content: '"→"',
                          position: 'absolute',
                          left: 0,
                          color: 'primary.main',
                          fontWeight: 600
                        }
                      }}
                    >
                      {example.translation}
                    </Typography>
                  )}
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Grammar Tip Section */}
        {explanation.grammar_tip && (
          <Box>
            <Chip 
              icon={<Psychology />} 
              label="Grammar Tip" 
              color="success" 
              variant="outlined"
              sx={{ 
                mb: 2, 
                fontWeight: 600,
                '& .MuiChip-icon': {
                  fontSize: '1.1rem'
                }
              }} 
            />
            <Typography 
              variant="body1" 
              sx={{ 
                pl: 1, 
                lineHeight: 1.7,
                color: 'text.primary',
                bgcolor: 'success.light',
                bgcolor: theme.palette.mode === 'dark' 
                  ? 'rgba(76, 175, 80, 0.08)' 
                  : 'rgba(76, 175, 80, 0.04)',
                p: 2,
                borderRadius: 1,
                border: `1px solid ${theme.palette.success.light}`,
              }}
            >
              {explanation.grammar_tip}
            </Typography>
          </Box>
        )}

        {/* Cultural Insight Section */}
        {explanation.cultural_insight && (
          <Box>
            <Chip 
              icon={<Public />} 
              label="Cultural Insight" 
              color="info" 
              variant="outlined"
              sx={{ 
                mb: 2, 
                fontWeight: 600,
                '& .MuiChip-icon': {
                  fontSize: '1.1rem'
                }
              }} 
            />
            <Typography 
              variant="body1" 
              sx={{ 
                pl: 1, 
                lineHeight: 1.7,
                color: 'text.primary',
                bgcolor: theme.palette.mode === 'dark' 
                  ? 'rgba(33, 150, 243, 0.08)' 
                  : 'rgba(33, 150, 243, 0.04)',
                p: 2,
                borderRadius: 1,
                border: `1px solid ${theme.palette.info.light}`,
                position: 'relative',
                '&::before': {
                  content: '"💡"',
                  position: 'absolute',
                  top: 8,
                  right: 12,
                  fontSize: '1.2rem',
                  opacity: 0.7
                }
              }}
            >
              {explanation.cultural_insight}
            </Typography>
          </Box>
        )}
      </Stack>

      {/* Footer with subtle branding */}
      <Box sx={{ mt: 3, pt: 2, borderTop: `1px solid ${theme.palette.divider}` }}>
        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            gap: 0.5
          }}
        >
          <Lightbulb sx={{ fontSize: '0.9rem' }} />
          Enhanced with AI-powered context retrieval
        </Typography>
      </Box>
    </Paper>
  );
};

export default LanguageTutor;