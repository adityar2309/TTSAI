import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';

const AdvancedTranslation = ({ translation, onSaveFlashcard }) => {
  const [activeTab, setActiveTab] = useState(0);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSaveFlashcard = () => {
    onSaveFlashcard(translation);
  };

  if (!translation) {
    return null;
  }

  return (
    <Card 
      elevation={0}
      sx={{
        mt: 2,
        background: theme.palette.mode === 'dark' 
          ? 'rgba(255, 255, 255, 0.05)' 
          : 'rgba(0, 0, 0, 0.02)',
        backdropFilter: 'blur(10px)',
        borderRadius: theme.shape.borderRadius,
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Translation Details
          </Typography>
          <Tooltip title="Save as flashcard">
            <IconButton onClick={handleSaveFlashcard} color="primary">
              <BookmarkBorderIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant={isMobile ? "scrollable" : "standard"}
          scrollButtons={isMobile ? "auto" : false}
          sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
        >
          <Tab label="Main" />
          <Tab label="Alternatives" />
          <Tab label="Pronunciation" />
          <Tab label="Grammar" />
          <Tab label="Context" />
        </Tabs>

        <Box sx={{ mt: 2 }}>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {translation.main_translation}
              </Typography>
            </Box>
          )}

          {activeTab === 1 && (
            <List>
              {translation.alternatives.map((alt, index) => (
                <ListItem key={index} alignItems="flex-start">
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body1">{alt.text}</Typography>
                        <Chip 
                          label={`${alt.confidence}%`}
                          size="small"
                          color={alt.confidence > 80 ? "success" : "primary"}
                        />
                      </Box>
                    }
                    secondary={alt.explanation}
                  />
                </ListItem>
              ))}
            </List>
          )}

          {activeTab === 2 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                IPA: {translation.pronunciation.ipa}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Syllables: {translation.pronunciation.syllables}
              </Typography>
              <Typography variant="subtitle1">
                Stress: {translation.pronunciation.stress}
              </Typography>
              {translation.pronunciation.phonetic && (
                <Typography variant="subtitle1" gutterBottom>
                  Phonetic: {translation.pronunciation.phonetic}
                </Typography>
              )}
              {translation.pronunciation.romanization && (
                <>
                  <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                    Romanization: <Box component="span" sx={{ fontStyle: 'italic', fontFamily: 'serif' }}>{translation.pronunciation.romanization}</Box>
                  </Typography>
                  {translation.pronunciation.romanization_system && (
                    <Typography variant="body2" color="text.secondary">
                      System: {translation.pronunciation.romanization_system}
                    </Typography>
                  )}
                </>
              )}
            </Box>
          )}

          {activeTab === 3 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Parts of Speech:
              </Typography>
              <List dense>
                {translation.grammar.parts_of_speech.map((part, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={part} />
                  </ListItem>
                ))}
              </List>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" gutterBottom>
                Structure:
              </Typography>
              <Typography variant="body2" paragraph>
                {translation.grammar.structure}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Grammar Rules:
              </Typography>
              <List dense>
                {translation.grammar.rules.map((rule, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={rule} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {activeTab === 4 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Common Usage:
              </Typography>
              <List dense>
                {translation.context.usage.map((use, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={use} />
                  </ListItem>
                ))}
              </List>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" gutterBottom>
                Examples:
              </Typography>
              <List dense>
                {translation.context.examples.map((example, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={example} />
                  </ListItem>
                ))}
              </List>
              {translation.context.cultural_notes && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle1" gutterBottom>
                    Cultural Notes:
                  </Typography>
                  <Typography variant="body2">
                    {translation.context.cultural_notes}
                  </Typography>
                </>
              )}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default AdvancedTranslation; 