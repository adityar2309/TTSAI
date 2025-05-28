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
  Collapse,
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
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Tabs
          value={activeView}
          onChange={(e, newValue) => setActiveView(newValue)}
          variant="fullWidth"
        >
          <Tab value="translate" icon={<TranslateIcon />} label="Translate" />
          <Tab value="learn" icon={<SchoolIcon />} label="Learn" />
        </Tabs>
      </Box>

      {activeView === 'translate' && (
        <Stack spacing={3}>
          {/* Language Selection */}
          <Paper elevation={2} sx={{ p: 2 }}>
            <Stack
              direction={isMobile ? "column" : "row"}
              spacing={2}
              alignItems="center"
            >
              <FormControl sx={{ minWidth: 160 }}>
                <InputLabel>From</InputLabel>
                <Select
                  value={sourceLang}
                  onChange={(e) => setSourceLang(e.target.value)}
                  label="From"
                  size="small"
                >
                  {languages.map((lang) => (
                    <MenuItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <IconButton onClick={handleSwapLanguages}>
                <SwapHorizIcon />
              </IconButton>

              <FormControl sx={{ minWidth: 160 }}>
                <InputLabel>To</InputLabel>
                <Select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  label="To"
                  size="small"
                >
                  {languages.map((lang) => (
                    <MenuItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>
          </Paper>

          {/* Original Text Display */}
          <Paper elevation={2} sx={{ p: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1} mb={1}>
              <Typography variant="subtitle2" color="text.secondary">
                Original Text
              </Typography>
              <IconButton size="small" onClick={() => handleCopyText(originalText)}>
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Stack>
            <Typography variant="body1" sx={getTextStyle(originalText, sourceLang)}>
              {originalText || 'Your text will appear here'}
            </Typography>
          </Paper>

          {/* Translated Text Display */}
          <Paper elevation={2} sx={{ p: 2 }}>
            <Stack direction="row" alignItems="center" spacing={1} mb={1}>
              <Typography variant="subtitle2" color="text.secondary">
                Translation
              </Typography>
              <Stack direction="row" spacing={1}>
                <IconButton size="small" onClick={() => handleCopyText(translatedText)}>
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
                {translatedText && (
                  <IconButton size="small" onClick={playTranslatedAudio}>
                    <PlayArrowIcon fontSize="small" />
                  </IconButton>
                )}
              </Stack>
            </Stack>
            <Typography variant="body1" sx={getTextStyle(translatedText, targetLang)}>
              {translatedText || 'Translation will appear here'}
            </Typography>
            {isNonRomanScript(targetLang) && romanizedText && (
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ mt: 1, fontStyle: 'italic' }}
              >
                {romanizedText}
              </Typography>
            )}
          </Paper>

          {/* Input Section */}
          <Paper elevation={2} sx={{ p: 2 }}>
            <Stack direction="row" spacing={2} alignItems="flex-start">
              <TextField
                fullWidth
                multiline
                rows={3}
                value={inputText}
                onChange={handleTextInput}
                placeholder="Type or speak your text..."
                variant="outlined"
                disabled={isRecording}
                size="small"
                sx={{ bgcolor: 'background.paper' }}
              />
              <Stack direction="column" spacing={1}>
                <IconButton
                  onClick={toggleRecording}
                  color={isRecording ? 'error' : 'primary'}
                  sx={{
                    width: 40,
                    height: 40,
                    bgcolor: isRecording ? 'error.light' : 'primary.light',
                  }}
                >
                  {isRecording ? <StopIcon /> : <MicIcon />}
                </IconButton>
                <IconButton
                  color="primary"
                  onClick={handleSubmit}
                  disabled={!inputText.trim() || isRecording || isTranslating}
                  sx={{
                    width: 40,
                    height: 40,
                    bgcolor: 'primary.light',
                  }}
                >
                  <SendIcon />
                </IconButton>
              </Stack>
            </Stack>
          </Paper>
        </Stack>
      )}

      {activeView === 'learn' && (
        <LearningTools
          userId={userId}
          language={targetLang}
        />
      )}

      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Translator; 