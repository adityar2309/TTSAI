import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Typography,
  TextField,
  Container,
  Stack,
  Divider,
  useTheme,
  useMediaQuery,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Snackbar,
  Alert,
  ListItemIcon,
  Tabs,
  Tab,
  Tooltip,
} from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import SendIcon from '@mui/icons-material/Send';
import HistoryIcon from '@mui/icons-material/History';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import StarIcon from '@mui/icons-material/Star';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DeleteIcon from '@mui/icons-material/Delete';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import ChatIcon from '@mui/icons-material/Chat';
import ForumIcon from '@mui/icons-material/Forum';
import PersonIcon from '@mui/icons-material/Person';
import TranslateIcon from '@mui/icons-material/Translate';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import SchoolIcon from '@mui/icons-material/School';
import axios from 'axios';
import { format } from 'date-fns';
import AdvancedTranslation from './AdvancedTranslation';
import LearningTools from './LearningTools';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Font family for different languages
const getFontFamily = (langCode) => {
  switch (langCode) {
    case 'hi':
      return '"Noto Sans Devanagari", "Hind", sans-serif';
    default:
      return 'inherit';
  }
};

// Text direction for different languages
const getTextDirection = (langCode) => {
  return 'ltr'; // Hindi is LTR, add RTL languages here if needed
};

// Formality levels for translation
const formalityLevels = [
  { value: 'formal', label: 'Formal' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'informal', label: 'Informal' },
];

// Language dialects
const dialects = {
  es: [
    { value: 'es-ES', label: 'Spain' },
    { value: 'es-MX', label: 'Mexico' },
    { value: 'es-AR', label: 'Argentina' },
  ],
  zh: [
    { value: 'zh-CN', label: 'Mainland China' },
    { value: 'zh-TW', label: 'Taiwan' },
    { value: 'zh-HK', label: 'Hong Kong' },
  ],
  // Add more dialects for other languages as needed
};

export const Translator = ({ initialMode = 'type' }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [languages, setLanguages] = useState([]);
  const [sourceLang, setSourceLang] = useState('');
  const [targetLang, setTargetLang] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [originalText, setOriginalText] = useState('');
  const [inputText, setInputText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [romanizedText, setRomanizedText] = useState('');
  const [recognition, setRecognition] = useState(null);
  const [error, setError] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('translationHistory');
    return saved ? JSON.parse(saved) : [];
  });
  const [favorites, setFavorites] = useState(() => {
    const saved = localStorage.getItem('translationFavorites');
    return saved ? JSON.parse(saved) : [];
  });
  const [showHistory, setShowHistory] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [isDetecting, setIsDetecting] = useState(false);
  const [showTextInput, setShowTextInput] = useState(true);
  const [isConversationMode, setIsConversationMode] = useState(false);
  const [conversation, setConversation] = useState(() => {
    const saved = localStorage.getItem('currentConversation');
    return saved ? JSON.parse(saved) : [];
  });
  const [conversations, setConversations] = useState(() => {
    const saved = localStorage.getItem('savedConversations');
    return saved ? JSON.parse(saved) : [];
  });
  const [showConversations, setShowConversations] = useState(false);
  const [translation, setTranslation] = useState(null);
  const [formality, setFormality] = useState('neutral');
  const [dialect, setDialect] = useState('');
  const [activeView, setActiveView] = useState('translate');
  const [userId] = useState('user123'); // In a real app, this would come from auth

  // Style for language-specific text
  const getTextStyle = useCallback((text, langCode) => ({
    fontFamily: getFontFamily(langCode),
    direction: getTextDirection(langCode),
    minHeight: 100,
    fontSize: langCode === 'hi' ? '1.1rem' : 'inherit', // Slightly larger font for Hindi
  }), []);

  // Fetch supported languages
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await axios.get(`${API_URL}/supported-languages`);
        setLanguages(response.data);
        // Set default languages after fetching
        if (response.data.length >= 2) {
          setSourceLang(response.data[0].code);
          setTargetLang(response.data[1].code);
        }
      } catch (err) {
        setError('Failed to fetch supported languages');
        console.error(err);
      }
    };
    fetchLanguages();
  }, []);

  // Initialize speech recognition
  useEffect(() => {
    if (window.webkitSpeechRecognition) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        setInputText(finalTranscript || interimTranscript);
      };

      recognition.onerror = (event) => {
        setError(`Speech recognition error: ${event.error}`);
        setIsRecording(false);
      };

      setRecognition(recognition);
    } else {
      setError('Speech recognition is not supported in this browser');
    }
  }, []);

  // Save history and favorites to localStorage when they change
  useEffect(() => {
    localStorage.setItem('translationHistory', JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    localStorage.setItem('translationFavorites', JSON.stringify(favorites));
  }, [favorites]);

  // Save conversation to localStorage
  useEffect(() => {
    localStorage.setItem('currentConversation', JSON.stringify(conversation));
  }, [conversation]);

  useEffect(() => {
    localStorage.setItem('savedConversations', JSON.stringify(conversations));
  }, [conversations]);

  // Update handleTranslation for conversation mode
  const handleTranslation = useCallback(async (text) => {
    if (!text) return;
    setIsTranslating(true);
    setError(null);

    try {
      // First detect the language if source is not specified
      if (!sourceLang) {
        const detectResponse = await axios.post(`${API_URL}/detect-language`, { text });
        if (detectResponse.data.detectedLanguage) {
          setSourceLang(detectResponse.data.detectedLanguage);
        }
      }

      const response = await axios.post(`${API_URL}/translate`, {
        text,
        sourceLang,
        targetLang,
        formality,
        dialect,
      });
      
      const translatedText = response.data.translatedText;
      
      setTranslatedText(translatedText);
      setOriginalText(text);

      // Add to history
      const newEntry = {
        id: Date.now(),
        originalText: text,
        translatedText,
        sourceLang: sourceLang || response.data.detectedSourceLanguage,
        targetLang,
        timestamp: new Date().toISOString(),
        formality,
        dialect,
      };

      setHistory(prev => [newEntry, ...prev].slice(0, 50));

      // Add to conversation if in conversation mode
      if (isConversationMode) {
        setConversation(prev => [...prev, {
          text,
          translation: translatedText,
          sourceLang: sourceLang || response.data.detectedSourceLanguage,
          targetLang,
          timestamp: new Date().toISOString(),
          isSource: true,
        }]);
      }

    } catch (err) {
      console.error('Translation error:', err);
      setError(err.response?.data?.error || 'Translation failed');
    } finally {
      setIsTranslating(false);
    }
  }, [sourceLang, targetLang, isConversationMode, formality, dialect]);

  // Play translated audio
  const playTranslatedAudio = async () => {
    try {
      const response = await axios.post(
        `${API_URL}/text-to-speech`,
        {
          text: translatedText,
          languageCode: targetLang,
        },
        { responseType: 'json' }
      );

      const audioContent = response.data.audioContent;
      const audioBlob = new Blob(
        [Uint8Array.from(audioContent.match(/.{1,2}/g).map(byte => parseInt(byte, 16)))],
        { type: 'audio/mp3' }
      );
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (err) {
      setError('Failed to play audio');
      console.error(err);
    }
  };

  // Update toggleRecording to handle input visibility
  const toggleRecording = () => {
    if (!recognition) return;

    if (isRecording) {
      recognition.stop();
      setShowTextInput(true);
    } else {
      setError(null);
      setShowTextInput(false);
      setInputText('');
      recognition.start();
    }
    setIsRecording(!isRecording);
  };

  // Handle submit
  const handleSubmit = () => {
    if (inputText.trim()) {
      handleTranslation(inputText.trim());
    }
  };

  // Swap languages
  const handleSwapLanguages = () => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setOriginalText(translatedText);
    setTranslatedText(originalText);
    setInputText('');
  };

  // Handle manual text input
  const handleTextInput = (e) => {
    setInputText(e.target.value);
  };

  // Helper function to determine if a language uses non-Roman script
  const isNonRomanScript = (langCode) => {
    return ['hi', 'zh', 'ko'].includes(langCode);
  };

  const handleCopyText = (text) => {
    navigator.clipboard.writeText(text);
    setNotification({
      open: true,
      message: 'Text copied to clipboard',
      severity: 'success'
    });
  };

  const toggleFavorite = (entry) => {
    const isFavorite = favorites.some(f => f.id === entry.id);
    if (isFavorite) {
      setFavorites(prev => prev.filter(f => f.id !== entry.id));
    } else {
      setFavorites(prev => [...prev, entry]);
    }
  };

  const deleteHistoryEntry = (id) => {
    setHistory(prev => prev.filter(entry => entry.id !== id));
  };

  const handleHistoryItemClick = (entry) => {
    setInputText(entry.originalText);
    setSourceLang(entry.sourceLang);
    setTargetLang(entry.targetLang);
    setShowHistory(false);
    handleTranslation(entry.originalText);
  };

  // Add language detection
  const detectLanguage = useCallback(async (text) => {
    if (!text) return;
    setIsDetecting(true);
    
    try {
      const response = await axios.post(`${API_URL}/detect-language`, { text });
      const detectedLang = response.data.detectedLanguage;
      
      if (detectedLang && languages.some(lang => lang.code === detectedLang)) {
        setSourceLang(detectedLang);
        setNotification({
          open: true,
          message: `Detected language: ${languages.find(l => l.code === detectedLang)?.name}`,
          severity: 'success'
        });
      }
    } catch (err) {
      console.error('Language detection failed:', err);
      setNotification({
        open: true,
        message: 'Language detection failed',
        severity: 'error'
      });
    } finally {
      setIsDetecting(false);
    }
  }, [languages]);

  // Add debounced auto-detection
  useEffect(() => {
    if (!inputText || inputText.length < 10) return;
    
    const timer = setTimeout(() => {
      detectLanguage(inputText);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [inputText, detectLanguage]);

  const startNewConversation = () => {
    if (conversation.length > 0) {
      const newConversation = {
        id: Date.now(),
        messages: conversation,
        timestamp: new Date().toISOString(),
        languages: [sourceLang, targetLang],
      };
      setConversations(prev => [newConversation, ...prev]);
    }
    setConversation([]);
  };

  const loadConversation = (conv) => {
    setConversation(conv.messages);
    if (conv.languages?.length === 2) {
      setSourceLang(conv.languages[0]);
      setTargetLang(conv.languages[1]);
    }
    setShowConversations(false);
  };

  const deleteConversation = (id) => {
    setConversations(prev => prev.filter(conv => conv.id !== id));
  };

  const MessageBubble = ({ message, isSource }) => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isSource ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          maxWidth: '80%',
          bgcolor: isSource ? 'primary.light' : 'grey.100',
          borderRadius: 2,
          p: 2,
          position: 'relative',
        }}
      >
        <Typography variant="body1" color={isSource ? 'primary.contrastText' : 'text.primary'}>
          {message.originalText}
        </Typography>
        <Typography 
          variant="body2" 
          color={isSource ? 'primary.contrastText' : 'text.secondary'}
          sx={{ mt: 1, fontStyle: 'italic' }}
        >
          {message.translatedText}
          {message.romanizedText && ` (${message.romanizedText})`}
        </Typography>
        <Typography 
          variant="caption" 
          color={isSource ? 'primary.contrastText' : 'text.secondary'}
          sx={{ 
            display: 'block',
            mt: 1,
            opacity: 0.8,
          }}
        >
          {format(new Date(message.timestamp), 'HH:mm')}
        </Typography>
      </Box>
    </Box>
  );

  const handleTranslate = async () => {
    if (!inputText.trim()) return;

    try {
      const response = await fetch('/api/advanced-translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          sourceLang,
          targetLang,
          formality,
          dialect: dialect || undefined,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setTranslation(data);
      } else {
        console.error('Translation error:', data.error);
      }
    } catch (error) {
      console.error('Translation request failed:', error);
    }
  };

  const handleSaveFlashcard = async (translationData) => {
    try {
      await fetch('/api/flashcards', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          translation: translationData,
        }),
      });
      // Show success message or update UI
    } catch (error) {
      console.error('Error saving flashcard:', error);
    }
  };

  return (
    <Container maxWidth="md" disableGutters={isMobile}>
      <Typography variant="h4" gutterBottom align="center" sx={{ mb: 4 }}>
        Real-Time Speech Translator
      </Typography>

      {error && (
        <Paper
          sx={{
            p: 1.5,
            mb: 2,
            mx: { xs: 1, sm: 0 },
            backgroundColor: 'error.light',
            color: 'error.contrastText',
          }}
        >
          {error}
        </Paper>
      )}

      <Tabs
        value={activeView}
        onChange={(e, newValue) => setActiveView(newValue)}
        sx={{ mb: 3 }}
        variant={isMobile ? "scrollable" : "standard"}
        scrollButtons={isMobile ? "auto" : false}
      >
        <Tab value="translate" icon={<TranslateIcon />} label="Translate" />
        <Tab value="learn" icon={<SchoolIcon />} label="Learn" />
      </Tabs>

      {activeView === 'translate' && (
        <>
          <Card
            elevation={0}
            sx={{
              background: theme.palette.mode === 'dark'
                ? 'rgba(255, 255, 255, 0.05)'
                : 'rgba(0, 0, 0, 0.02)',
              backdropFilter: 'blur(10px)',
            }}
          >
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Source Language</InputLabel>
                    <Select
                      value={sourceLang}
                      onChange={(e) => setSourceLang(e.target.value)}
                      label="Source Language"
                    >
                      {languages.map((lang) => (
                        <MenuItem key={lang.code} value={lang.code}>
                          {lang.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Target Language</InputLabel>
                    <Select
                      value={targetLang}
                      onChange={(e) => setTargetLang(e.target.value)}
                      label="Target Language"
                    >
                      {languages.map((lang) => (
                        <MenuItem key={lang.code} value={lang.code}>
                          {lang.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Formality</InputLabel>
                    <Select
                      value={formality}
                      onChange={(e) => setFormality(e.target.value)}
                      label="Formality"
                    >
                      {formalityLevels.map((level) => (
                        <MenuItem key={level.value} value={level.value}>
                          {level.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Dialect</InputLabel>
                    <Select
                      value={dialect}
                      onChange={(e) => setDialect(e.target.value)}
                      label="Dialect"
                      disabled={!dialects[targetLang]}
                    >
                      <MenuItem value="">
                        <em>Standard</em>
                      </MenuItem>
                      {dialects[targetLang]?.map((d) => (
                        <MenuItem key={d.value} value={d.value}>
                          {d.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <TextField
                fullWidth
                multiline
                rows={4}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter text to translate..."
                sx={{ mb: 2 }}
              />

              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Button
                  variant="contained"
                  onClick={handleTranslate}
                  disabled={!inputText.trim()}
                  sx={{ flex: 1 }}
                >
                  Translate
                </Button>
                <Tooltip title={isRecording ? 'Stop Recording' : 'Start Recording'}>
                  <IconButton
                    color={isRecording ? 'error' : 'primary'}
                    onClick={toggleRecording}
                  >
                    {isRecording ? <StopIcon /> : <MicIcon />}
                  </IconButton>
                </Tooltip>
              </Box>
            </CardContent>
          </Card>

          {translation && (
            <AdvancedTranslation
              translation={translation}
              onSaveFlashcard={handleSaveFlashcard}
            />
          )}
        </>
      )}

      {activeView === 'learn' && (
        <LearningTools
          userId={userId}
          language={targetLang}
        />
      )}

      <Grid container spacing={isMobile ? 1 : 3}>
        {/* Language Selection */}
        <Grid item xs={12}>
          <Paper sx={{ p: { xs: 1, sm: 2 } }}>
            <Stack
              direction={isMobile ? "column" : "row"}
              spacing={isMobile ? 1 : 2}
              alignItems="center"
              justifyContent="center"
            >
              <FormControl fullWidth={isMobile} sx={{ minWidth: isMobile ? '100%' : 200 }}>
                <InputLabel>Source Language</InputLabel>
                <Select
                  value={sourceLang}
                  onChange={(e) => setSourceLang(e.target.value)}
                  label="Source Language"
                  disabled={languages.length === 0}
                  size={isMobile ? "small" : "medium"}
                  endAdornment={
                    <IconButton
                      size="small"
                      onClick={() => detectLanguage(inputText)}
                      disabled={!inputText || isDetecting}
                      sx={{ mr: 2 }}
                      title="Auto-detect language"
                    >
                      <AutorenewIcon fontSize="small" />
                    </IconButton>
                  }
                >
                  {languages.map((lang) => (
                    <MenuItem 
                      key={lang.code} 
                      value={lang.code}
                      sx={{ fontFamily: getFontFamily(lang.code) }}
                    >
                      {lang.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <IconButton 
                onClick={handleSwapLanguages}
                disabled={languages.length === 0}
                sx={{ transform: isMobile ? 'rotate(90deg)' : 'none' }}
              >
                <SwapHorizIcon />
              </IconButton>

              <FormControl fullWidth={isMobile} sx={{ minWidth: isMobile ? '100%' : 200 }}>
                <InputLabel>Target Language</InputLabel>
                <Select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  label="Target Language"
                  disabled={languages.length === 0}
                  size={isMobile ? "small" : "medium"}
                >
                  {languages.map((lang) => (
                    <MenuItem 
                      key={lang.code} 
                      value={lang.code}
                      sx={{ fontFamily: getFontFamily(lang.code) }}
                    >
                      {lang.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Stack direction="row" spacing={1}>
                <IconButton
                  onClick={() => setShowHistory(true)}
                  color="primary"
                  title="Translation History"
                >
                  <HistoryIcon />
                </IconButton>
                <IconButton
                  onClick={() => setShowConversations(true)}
                  color={isConversationMode ? "primary" : "default"}
                  title="Saved Conversations"
                >
                  <ForumIcon />
                </IconButton>
                <IconButton
                  onClick={() => {
                    if (isConversationMode && conversation.length > 0) {
                      startNewConversation();
                    }
                    setIsConversationMode(!isConversationMode);
                  }}
                  color={isConversationMode ? "primary" : "default"}
                  title={isConversationMode ? "Switch to Single Translation" : "Switch to Conversation Mode"}
                >
                  <ChatIcon />
                </IconButton>
              </Stack>
            </Stack>
          </Paper>
        </Grid>

        {/* Conversation or Translation Cards */}
        {isConversationMode ? (
          <Grid item xs={12}>
            <Paper 
              sx={{ 
                p: { xs: 1.5, sm: 2 },
                minHeight: 300,
                maxHeight: 500,
                overflow: 'auto',
              }}
            >
              {conversation.length === 0 ? (
                <Box
                  sx={{
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography color="text.secondary">
                    Start your conversation by typing or speaking
                  </Typography>
                </Box>
              ) : (
                conversation.map((message) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    isSource={message.sourceLang === sourceLang}
                  />
                ))
              )}
            </Paper>
          </Grid>
        ) : (
          <>
            {/* Translation Cards */}
            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ p: { xs: 1.5, sm: 2 } }}>
                  <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                      Original Text
                    </Typography>
                    <IconButton
                      onClick={() => handleCopyText(originalText)}
                      size={isMobile ? "small" : "medium"}
                      title="Copy text"
                    >
                      <ContentCopyIcon />
                    </IconButton>
                  </Stack>
                  <Typography 
                    variant="body1" 
                    sx={{
                      ...getTextStyle(originalText, sourceLang),
                      minHeight: { xs: 60, sm: 100 },
                    }}
                  >
                    {originalText}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ p: { xs: 1.5, sm: 2 } }}>
                  <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                      Translated Text
                    </Typography>
                    <IconButton
                      onClick={() => handleCopyText(translatedText)}
                      size={isMobile ? "small" : "medium"}
                      title="Copy text"
                    >
                      <ContentCopyIcon />
                    </IconButton>
                    <IconButton
                      onClick={playTranslatedAudio}
                      disabled={!translatedText}
                      color="primary"
                      size={isMobile ? "small" : "medium"}
                    >
                      <PlayArrowIcon />
                    </IconButton>
                  </Stack>
                  <Box sx={{ mb: isNonRomanScript(targetLang) && romanizedText ? 2 : 0 }}>
                    <Typography 
                      variant="body1" 
                      sx={{
                        ...getTextStyle(translatedText, targetLang),
                        mb: 1,
                      }}
                    >
                      {translatedText}
                    </Typography>
                    {isNonRomanScript(targetLang) && romanizedText && (
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Typography 
                          variant="body2" 
                          color="text.secondary"
                          sx={{
                            fontStyle: 'italic',
                            pl: 1,
                            borderLeft: '2px solid',
                            borderColor: 'divider',
                            flexGrow: 1,
                          }}
                        >
                          {romanizedText}
                        </Typography>
                        <IconButton
                          onClick={() => handleCopyText(romanizedText)}
                          size="small"
                          title="Copy romanized text"
                        >
                          <ContentCopyIcon fontSize="small" />
                        </IconButton>
                      </Stack>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}

        {/* Unified Input Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: { xs: 1.5, sm: 2 } }}>
            <Stack direction="row" spacing={1} alignItems="flex-start">
              {showTextInput ? (
                <TextField
                  fullWidth
                  multiline
                  rows={isMobile ? 3 : 2}
                  value={inputText}
                  onChange={handleTextInput}
                  placeholder="Type or click the microphone to speak..."
                  variant="outlined"
                  disabled={isRecording}
                  size={isMobile ? "small" : "medium"}
                  InputProps={{
                    style: {
                      fontFamily: getFontFamily(sourceLang),
                      direction: getTextDirection(sourceLang),
                      fontSize: sourceLang === 'hi' ? '1.1rem' : 'inherit',
                    },
                  }}
                />
              ) : (
                <Box
                  sx={{
                    flexGrow: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: isMobile ? 120 : 100,
                    bgcolor: 'action.hover',
                    borderRadius: 1,
                    p: 2,
                  }}
                >
                  <Typography
                    variant="body1"
                    color="text.secondary"
                    align="center"
                  >
                    {inputText || "Listening..."}
                  </Typography>
                </Box>
              )}
              <Stack direction={isMobile ? "row" : "column"} spacing={1}>
                <IconButton
                  onClick={toggleRecording}
                  color={isRecording ? 'error' : 'primary'}
                  sx={{
                    width: { xs: 40, sm: 56 },
                    height: { xs: 40, sm: 56 },
                    backgroundColor: isRecording ? 'error.light' : 'primary.light',
                    '&:hover': {
                      backgroundColor: isRecording ? 'error.main' : 'primary.main',
                    },
                  }}
                >
                  {isRecording ? <StopIcon /> : <MicIcon />}
                </IconButton>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSubmit}
                  disabled={!inputText.trim() || isRecording || isTranslating}
                  sx={{
                    height: { xs: 40, sm: 56 },
                    minWidth: { xs: 40, sm: 56 },
                    p: { xs: 1, sm: 2 },
                  }}
                >
                  <SendIcon />
                </Button>
              </Stack>
            </Stack>
          </Paper>
        </Grid>
      </Grid>

      {/* Saved Conversations Dialog */}
      <Dialog
        open={showConversations}
        onClose={() => setShowConversations(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Stack direction="row" alignItems="center" spacing={1}>
            <ForumIcon />
            <Typography>Saved Conversations</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          {conversations.length === 0 ? (
            <Typography color="text.secondary" align="center" sx={{ py: 2 }}>
              No saved conversations yet
            </Typography>
          ) : (
            <List>
              {conversations.map((conv) => (
                <ListItem
                  key={conv.id}
                  button
                  onClick={() => loadConversation(conv)}
                >
                  <ListItemIcon>
                    <ChatIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={`Conversation from ${format(new Date(conv.timestamp), 'MMM d, yyyy HH:mm')}`}
                    secondary={`${conv.messages.length} messages`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteConversation(conv.id);
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
      </Dialog>

      {/* History Dialog */}
      <Dialog
        open={showHistory}
        onClose={() => setShowHistory(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Translation History</DialogTitle>
        <DialogContent>
          <List>
            {[...favorites, ...history.filter(h => !favorites.some(f => f.id === h.id))].map((entry) => (
              <ListItem
                key={entry.id}
                button
                onClick={() => handleHistoryItemClick(entry)}
              >
                <ListItemText
                  primary={entry.originalText}
                  secondary={
                    <React.Fragment>
                      <Typography variant="body2" color="text.secondary">
                        {entry.translatedText}
                        {entry.romanizedText && ` (${entry.romanizedText})`}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(entry.timestamp).toLocaleString()}
                      </Typography>
                    </React.Fragment>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => toggleFavorite(entry)}
                    title={favorites.some(f => f.id === entry.id) ? "Remove from favorites" : "Add to favorites"}
                  >
                    {favorites.some(f => f.id === entry.id) ? <StarIcon color="primary" /> : <StarBorderIcon />}
                  </IconButton>
                  <IconButton
                    edge="end"
                    onClick={() => deleteHistoryEntry(entry.id)}
                    title="Delete from history"
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DialogContent>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert
          onClose={() => setNotification({ ...notification, open: false })}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Translator; 