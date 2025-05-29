import React, { useState, useEffect, useCallback, useRef } from 'react';
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
  Chip,
  CircularProgress,
  LinearProgress,
  Badge,
  Avatar,
  Menu,
  DialogActions,
  Slider,
  Switch,
  FormControlLabel,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
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
import SettingsIcon from '@mui/icons-material/Settings';
import TuneIcon from '@mui/icons-material/Tune';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import ImageIcon from '@mui/icons-material/Image';
import MicOffIcon from '@mui/icons-material/MicOff';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import InfoIcon from '@mui/icons-material/Info';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import LanguageIcon from '@mui/icons-material/Language';
import PauseIcon from '@mui/icons-material/Pause';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import axios from 'axios';
import { format } from 'date-fns';
import AdvancedTranslation from './AdvancedTranslation';
import LearningTools from './LearningTools';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Enhanced font family mapping for different languages
const getFontFamily = (langCode) => {
  const fontMap = {
    'hi': '"Noto Sans Devanagari", "Hind", "Mangal", sans-serif',
    'ar': '"Noto Sans Arabic", "Arabic UI Text", sans-serif',
    'zh': '"Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", sans-serif',
    'zh-TW': '"Noto Sans CJK TC", "PingFang TC", "Microsoft JhengHei", sans-serif',
    'ja': '"Noto Sans CJK JP", "Hiragino Kaku Gothic Pro", "Yu Gothic", sans-serif',
    'ko': '"Noto Sans CJK KR", "Malgun Gothic", "Apple Gothic", sans-serif',
    'th': '"Noto Sans Thai", "Leelawadee UI", sans-serif',
    'he': '"Noto Sans Hebrew", "Arial Hebrew", sans-serif',
    'ru': '"Noto Sans", "Segoe UI", "Arial", sans-serif',
    'default': '"Roboto", "Helvetica", "Arial", sans-serif'
  };
  return fontMap[langCode] || fontMap.default;
};

// Text direction for different languages
const getTextDirection = (langCode) => {
  const rtlLanguages = ['ar', 'he', 'ur', 'fa'];
  return rtlLanguages.includes(langCode) ? 'rtl' : 'ltr';
};

// Enhanced formality levels
const formalityLevels = [
  { value: 'formal', label: 'Formal', icon: '🎩', description: 'Business, academic, official' },
  { value: 'neutral', label: 'Neutral', icon: '😊', description: 'Standard, everyday conversation' },
  { value: 'informal', label: 'Casual', icon: '😎', description: 'Friendly, relaxed, slang' },
];

// Enhanced language dialects with more options
const dialects = {
  es: [
    { value: 'es-ES', label: 'Spain (European)', flag: '🇪🇸' },
    { value: 'es-MX', label: 'Mexico', flag: '🇲🇽' },
    { value: 'es-AR', label: 'Argentina', flag: '🇦🇷' },
    { value: 'es-CO', label: 'Colombia', flag: '🇨🇴' },
    { value: 'es-CL', label: 'Chile', flag: '🇨🇱' },
    { value: 'es-PE', label: 'Peru', flag: '🇵🇪' },
  ],
  en: [
    { value: 'en-US', label: 'United States', flag: '🇺🇸' },
    { value: 'en-GB', label: 'United Kingdom', flag: '🇬🇧' },
    { value: 'en-AU', label: 'Australia', flag: '🇦🇺' },
    { value: 'en-CA', label: 'Canada', flag: '🇨🇦' },
    { value: 'en-IN', label: 'India', flag: '🇮🇳' },
  ],
  fr: [
    { value: 'fr-FR', label: 'France', flag: '🇫🇷' },
    { value: 'fr-CA', label: 'Canada', flag: '🇨🇦' },
    { value: 'fr-BE', label: 'Belgium', flag: '🇧🇪' },
    { value: 'fr-CH', label: 'Switzerland', flag: '🇨🇭' },
  ],
  zh: [
    { value: 'zh-CN', label: 'Mainland China (Simplified)', flag: '🇨🇳' },
    { value: 'zh-TW', label: 'Taiwan (Traditional)', flag: '🇹🇼' },
    { value: 'zh-HK', label: 'Hong Kong (Traditional)', flag: '🇭🇰' },
    { value: 'zh-SG', label: 'Singapore', flag: '🇸🇬' },
  ],
  pt: [
    { value: 'pt-BR', label: 'Brazil', flag: '🇧🇷' },
    { value: 'pt-PT', label: 'Portugal', flag: '🇵🇹' },
  ],
  ar: [
    { value: 'ar-SA', label: 'Saudi Arabia', flag: '🇸🇦' },
    { value: 'ar-EG', label: 'Egypt', flag: '🇪🇬' },
    { value: 'ar-AE', label: 'UAE', flag: '🇦🇪' },
    { value: 'ar-MA', label: 'Morocco', flag: '🇲🇦' },
  ],
};

// Voice options for TTS
const voiceOptions = [
  { value: 'NEUTRAL', label: 'Neutral', icon: '🤖' },
  { value: 'FEMALE', label: 'Female', icon: '👩' },
  { value: 'MALE', label: 'Male', icon: '👨' },
];

export const Translator = ({ initialMode = 'type' }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  
  // Core state
  const [languages, setLanguages] = useState([]);
  const [sourceLang, setSourceLang] = useState('');
  const [targetLang, setTargetLang] = useState('');
  const [inputText, setInputText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [translation, setTranslation] = useState(null);
  
  // Romanization state
  const [romanizationData, setRomanizationData] = useState(null);
  
  // UI state
  const [activeView, setActiveView] = useState('translate');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [error, setError] = useState(null);
  
  // Speech recognition state
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  
  // Settings and preferences
  const [formality, setFormality] = useState('neutral');
  const [dialect, setDialect] = useState('');
  const [voiceGender, setVoiceGender] = useState('NEUTRAL');
  const [speechSpeed, setSpeechSpeed] = useState(1.0);
  const [autoPlayTranslations, setAutoPlayTranslations] = useState(true);
  const [showTextInput, setShowTextInput] = useState(true);
  
  // History and favorites
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('translationHistory');
    return saved ? JSON.parse(saved) : [];
  });
  const [favorites, setFavorites] = useState(() => {
    const saved = localStorage.getItem('translationFavorites');
    return saved ? JSON.parse(saved) : [];
  });
  const [showHistory, setShowHistory] = useState(false);
  
  // Conversation mode
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
  
  // Settings dialog
  const [showSettings, setShowSettings] = useState(false);
  const [settingsTab, setSettingsTab] = useState(0);
  
  // Other state
  const [userId] = useState('user123'); // In a real app, this would come from auth
  const [sessionId] = useState(Date.now().toString());
  const [progressBarProgress, setProgressBarProgress] = useState(0);
  const [characterCount, setCharacterCount] = useState(0);
  const characterLimit = 1000;
  
  // Refs
  const inputRef = useRef(null);
  const audioRef = useRef(null);

  // Enhanced text style function
  const getTextStyle = useCallback((text, langCode) => ({
    fontFamily: getFontFamily(langCode),
    direction: getTextDirection(langCode),
    minHeight: isMobile ? 80 : 100,
    fontSize: langCode === 'hi' ? '1.1rem' : 'inherit',
    lineHeight: 1.6,
    padding: theme.spacing(1),
  }), [isMobile, theme]);

  // Initialize speech recognition with enhanced features
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 3;
      
      recognition.onstart = () => {
        setIsRecording(true);
        recordAnalytics('speech_recognition_started');
      };
      
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

        const currentText = finalTranscript || interimTranscript;
        setInputText(currentText);
        setCharacterCount(currentText.length);
        
        // Auto-detect language if enabled
        if (finalTranscript && sourceLang === 'auto') {
          detectLanguage(finalTranscript);
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setError(`Speech recognition error: ${event.error}`);
        setIsRecording(false);
        recordAnalytics('speech_recognition_error', { error: event.error });
      };
      
      recognition.onend = () => {
        setIsRecording(false);
        recordAnalytics('speech_recognition_ended');
      };

      setRecognition(recognition);
      setSpeechSupported(true);
    } else {
      setSpeechSupported(false);
      setError('Speech recognition is not supported in this browser');
    }
  }, [sourceLang]);

  // Fetch supported languages with enhanced data
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await axios.get(`${API_URL}/supported-languages`);
        const languageData = response.data.languages || response.data;
        setLanguages(languageData);
        
        // Set default languages with user preferences
        const userPrefs = await fetchUserPreferences();
        if (languageData.length >= 2) {
          setSourceLang(userPrefs?.default_source_lang || languageData[0].code);
          setTargetLang(userPrefs?.default_target_lang || languageData[1].code);
        }
      } catch (err) {
        setError('Failed to fetch supported languages');
        console.error('Language fetch error:', err);
      }
    };
    fetchLanguages();
  }, []);

  // Auto-save history and favorites
  useEffect(() => {
    localStorage.setItem('translationHistory', JSON.stringify(history));
  }, [history]);

  useEffect(() => {
    localStorage.setItem('translationFavorites', JSON.stringify(favorites));
  }, [favorites]);

  useEffect(() => {
    localStorage.setItem('currentConversation', JSON.stringify(conversation));
  }, [conversation]);

  useEffect(() => {
    localStorage.setItem('savedConversations', JSON.stringify(conversations));
  }, [conversations]);

  // Fetch user preferences
  const fetchUserPreferences = async () => {
    try {
      const response = await axios.get(`${API_URL}/user/preferences?userId=${userId}`);
      const prefs = response.data;
      
      // Apply preferences
      setFormality(prefs.formality || 'neutral');
      setVoiceGender(prefs.voice_gender || 'NEUTRAL');
      setSpeechSpeed(prefs.speech_speed || 1.0);
      setAutoPlayTranslations(prefs.auto_play_translations !== false);
      
      return prefs;
    } catch (err) {
      console.error('Failed to fetch user preferences:', err);
      return {};
    }
  };

  // Save user preferences
  const saveUserPreferences = async (preferences) => {
    try {
      await axios.post(`${API_URL}/user/preferences`, {
        userId,
        ...preferences
      });
      showNotification('Settings saved successfully', 'success');
    } catch (err) {
      console.error('Failed to save preferences:', err);
      showNotification('Failed to save settings', 'error');
    }
  };

  // Record analytics
  const recordAnalytics = async (eventType, eventData = {}) => {
    try {
      await axios.post(`${API_URL}/analytics`, {
        userId,
        sessionId,
        eventType,
        eventData
      });
    } catch (err) {
      console.error('Analytics recording failed:', err);
    }
  };

  // Enhanced language detection
  const detectLanguage = async (text) => {
    if (!text || text.length < 3) return;
    
    setIsDetecting(true);
    try {
      const response = await axios.post(`${API_URL}/detect-language`, { text });
      const detected = response.data.detected_language;
      
      if (detected && detected !== sourceLang) {
        setSourceLang(detected);
        showNotification(`Language detected: ${getLanguageName(detected)}`, 'info');
        recordAnalytics('language_detected', { detected, confidence: response.data.confidence });
      }
    } catch (err) {
      console.error('Language detection failed:', err);
    } finally {
      setIsDetecting(false);
    }
  };

  // Get language name from code
  const getLanguageName = (code) => {
    const lang = languages.find(l => l.code === code);
    return lang ? lang.name : code;
  };

  // Enhanced translation function
  const handleTranslate = async (useAdvanced = false) => {
    if (!inputText.trim() || !sourceLang || !targetLang) {
      showNotification('Please enter text and select languages', 'warning');
      return;
    }

    setIsTranslating(true);
    setProgressBarProgress(0);
    
    // Animate progress bar
    const progressInterval = setInterval(() => {
      setProgressBarProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const endpoint = useAdvanced ? 'advanced-translate' : 'translate';
      const payload = {
        text: inputText.trim(),
        sourceLang,
        targetLang,
        formality,
        dialect: dialect || undefined,
        context: isConversationMode ? 'conversation' : undefined
      };

      recordAnalytics('translation_started', { 
        ...payload, 
        advanced: useAdvanced,
        character_count: inputText.length 
      });

      const response = await axios.post(`${API_URL}/${endpoint}`, payload);
      const data = response.data;

      clearInterval(progressInterval);
      setProgressBarProgress(100);

      if (useAdvanced) {
        setTranslation(data);
        setShowAdvanced(true);
        setTranslatedText(data.main_translation);
        // Store romanization from advanced translation
        if (data.pronunciation && data.pronunciation.romanization) {
          setRomanizationData({
            romanization: data.pronunciation.romanization,
            romanization_system: data.pronunciation.romanization_system
          });
        } else {
          setRomanizationData(null);
        }
      } else {
        setTranslatedText(data.translation);
        setTranslation(null);
        // Store romanization from basic translation
        if (data.romanization) {
          setRomanizationData({
            romanization: data.romanization,
            romanization_system: data.romanization_system
          });
        } else {
          setRomanizationData(null);
        }
      }

      // Add to history
      const historyEntry = {
        id: Date.now(),
        original: inputText,
        translated: data.main_translation || data.translation,
        sourceLang,
        targetLang,
        timestamp: new Date().toISOString(),
        formality,
        dialect,
        advanced: useAdvanced
      };

      setHistory(prev => [historyEntry, ...prev.slice(0, 99)]); // Keep last 100

      // Add to conversation if in conversation mode
      if (isConversationMode) {
        const message = {
          id: Date.now(),
          text: inputText,
          translation: data.main_translation || data.translation,
          isSource: true,
          timestamp: new Date().toISOString(),
          sourceLang,
          targetLang
        };
        setConversation(prev => [...prev, message]);
      }

      // Auto-play translation if enabled
      if (autoPlayTranslations && (data.main_translation || data.translation)) {
        playTranslatedAudio(data.main_translation || data.translation);
      }

      recordAnalytics('translation_completed', { 
        success: true,
        advanced: useAdvanced,
        character_count: inputText.length 
      });

      showNotification('Translation completed!', 'success');

    } catch (err) {
      clearInterval(progressInterval);
      setProgressBarProgress(0);
      
      const errorMessage = err.response?.data?.error || 'Translation failed';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
      
      recordAnalytics('translation_failed', { 
        error: errorMessage,
        character_count: inputText.length 
      });
    } finally {
      setIsTranslating(false);
      setTimeout(() => setProgressBarProgress(0), 1000);
    }
  };

  // Enhanced TTS function with caching
  const playTranslatedAudio = async (text, langCode = targetLang) => {
    if (!text) return;

    try {
      const response = await axios.post(`${API_URL}/text-to-speech`, {
        text,
        languageCode: langCode,
        voiceGender,
        speed: speechSpeed,
        pitch: 0.0
      });

      const audioContent = response.data.audio_content;
      if (audioContent) {
        const audio = new Audio(`data:audio/mp3;base64,${audioContent}`);
        audioRef.current = audio;
        
        audio.onplay = () => recordAnalytics('tts_played', { language: langCode });
        audio.onerror = () => showNotification('Audio playback failed', 'error');
      
      await audio.play();
      }
    } catch (err) {
      console.error('TTS error:', err);
      showNotification('Audio generation failed', 'error');
    }
  };

  // Enhanced utility functions
  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleSwapLanguages = () => {
    const tempLang = sourceLang;
    setSourceLang(targetLang);
    setTargetLang(tempLang);
    
    // Swap text if translation exists
    if (translatedText && inputText) {
      const tempText = inputText;
      setInputText(translatedText);
      setTranslatedText(tempText);
    }
    
    // Clear romanization data when swapping
    setRomanizationData(null);
    
    recordAnalytics('languages_swapped');
  };

  const handleCopyText = (text) => {
    navigator.clipboard.writeText(text);
    showNotification('Text copied to clipboard', 'success');
    recordAnalytics('text_copied');
  };

  const toggleFavorite = (entry) => {
    const isFavorite = favorites.some(f => f.id === entry.id);
    if (isFavorite) {
      setFavorites(prev => prev.filter(f => f.id !== entry.id));
      showNotification('Removed from favorites', 'info');
    } else {
      setFavorites(prev => [...prev, entry]);
      showNotification('Added to favorites', 'success');
    }
    recordAnalytics('favorite_toggled', { action: isFavorite ? 'remove' : 'add' });
  };

  const deleteHistoryEntry = (id) => {
    setHistory(prev => prev.filter(entry => entry.id !== id));
    showNotification('Entry removed from history', 'info');
  };

  const clearAllHistory = () => {
    setHistory([]);
    showNotification('History cleared', 'info');
    recordAnalytics('history_cleared');
  };

  const handleHistoryItemClick = (entry) => {
    setInputText(entry.original);
    setSourceLang(entry.sourceLang);
    setTargetLang(entry.targetLang);
    setTranslatedText(entry.translated);
    setShowHistory(false);
    recordAnalytics('history_item_selected');
  };

  const toggleRecording = () => {
    if (!recognition) {
      showNotification('Speech recognition not supported', 'error');
      return;
    }

    if (isRecording) {
      recognition.stop();
    } else {
      setError(null);
      recognition.lang = sourceLang || 'en';
      recognition.start();
    }
  };

  const handleTextChange = (e) => {
    const text = e.target.value;
    if (text.length <= characterLimit) {
      setInputText(text);
      setCharacterCount(text.length);
      
      // Clear romanization when input text is cleared or changed significantly
      if (text.length === 0 || Math.abs(text.length - inputText.length) > 10) {
        setRomanizationData(null);
      }
      
      // Auto-detect language for longer text
      if (text.length > 20 && sourceLang === 'auto') {
        detectLanguage(text);
      }
    }
  };

  // Conversation mode functions
  const startNewConversation = () => {
    if (conversation.length > 0) {
      const newConversation = {
        id: Date.now(),
        messages: conversation,
        timestamp: new Date().toISOString(),
        languages: [sourceLang, targetLang],
        title: `Conversation ${format(new Date(), 'MMM dd, HH:mm')}`
      };
      setConversations(prev => [newConversation, ...prev.slice(0, 19)]); // Keep last 20
    }
    setConversation([]);
    showNotification('New conversation started', 'info');
  };

  const loadConversation = (conv) => {
    setConversation(conv.messages);
    if (conv.languages?.length === 2) {
      setSourceLang(conv.languages[0]);
      setTargetLang(conv.languages[1]);
    }
    setShowConversations(false);
    showNotification('Conversation loaded', 'success');
  };

  const deleteConversation = (id) => {
    setConversations(prev => prev.filter(conv => conv.id !== id));
    showNotification('Conversation deleted', 'info');
  };

  // Settings functions
  const handleSettingsChange = (setting, value) => {
    const settings = {
      formality: setFormality,
      dialect: setDialect,
      voiceGender: setVoiceGender,
      speechSpeed: setSpeechSpeed,
      autoPlayTranslations: setAutoPlayTranslations,
    };

    if (settings[setting]) {
      settings[setting](value);
      
      // Save to backend
      saveUserPreferences({
        [setting]: value
      });
    }
  };

  // Advanced features
  const saveAsFlashcard = async () => {
    if (!inputText || !translatedText) {
      showNotification('Need both original and translated text', 'warning');
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/flashcards`, {
        userId,
        translation: {
          original: inputText,
          translated: translatedText,
          sourceLang,
          targetLang
        },
        difficulty: 'beginner',
        category: 'general'
      });

      if (response.data.success) {
        showNotification('Saved as flashcard!', 'success');
        recordAnalytics('flashcard_created');
      }
    } catch (err) {
      console.error('Flashcard save error:', err);
      showNotification('Failed to save flashcard', 'error');
    }
  };

  const MessageBubble = ({ message }) => (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: message.isSource ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Paper
        elevation={1}
        sx={{
          maxWidth: '80%',
          bgcolor: message.isSource ? 'primary.light' : 'grey.100',
          borderRadius: 2,
          p: 2,
        }}
      >
        <Typography 
          variant="body1" 
          color={message.isSource ? 'primary.contrastText' : 'text.primary'}
          sx={getTextStyle(message.text, message.sourceLang)}
        >
          {message.text}
        </Typography>
        <Typography 
          variant="body2" 
          color={message.isSource ? 'primary.contrastText' : 'text.secondary'}
          sx={{ mt: 1, fontStyle: 'italic', ...getTextStyle(message.translation, message.targetLang) }}
        >
          {message.translation}
        </Typography>
        <Typography 
          variant="caption" 
          color={message.isSource ? 'primary.contrastText' : 'text.secondary'}
          sx={{ display: 'block', mt: 1, opacity: 0.8 }}
        >
          {format(new Date(message.timestamp), 'HH:mm')}
        </Typography>
      </Paper>
    </Box>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      {/* Progress Bar */}
      {progressBarProgress > 0 && (
        <LinearProgress 
          variant="determinate" 
          value={progressBarProgress} 
          sx={{ mb: 2, height: 4, borderRadius: 2 }}
        />
      )}

      {/* Main Content */}
      <Box sx={{ mb: 3 }}>
        <Tabs
          value={activeView}
          onChange={(e, newValue) => setActiveView(newValue)}
          variant="fullWidth"
          sx={{ mb: 3 }}
        >
          <Tab 
            icon={<TranslateIcon />} 
            label="Translate" 
            value="translate"
          />
          <Tab 
            icon={<ChatIcon />} 
            label="Conversation" 
            value="conversation"
          />
          <Tab 
            icon={<SchoolIcon />} 
            label="Learning" 
            value="learning"
          />
        </Tabs>

        {/* Translation View */}
      {activeView === 'translate' && (
        <Stack spacing={3}>
          {/* Language Selection */}
            <Card elevation={2}>
              <CardContent>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={5}>
                    <FormControl fullWidth>
                <InputLabel>From</InputLabel>
                <Select
                  value={sourceLang}
                  onChange={(e) => setSourceLang(e.target.value)}
                  label="From"
                        startAdornment={
                          isDetecting && (
                            <CircularProgress size={16} sx={{ mr: 1 }} />
                          )
                        }
                      >
                        <MenuItem value="auto">
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <AutorenewIcon fontSize="small" />
                            Auto-detect
                          </Box>
                        </MenuItem>
                  {languages.map((lang) => (
                    <MenuItem key={lang.code} value={lang.code}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography>{lang.native_name || lang.name}</Typography>
                              {lang.tts_supported && <VolumeUpIcon fontSize="small" color="action" />}
                              {lang.speech_recognition_supported && <MicIcon fontSize="small" color="action" />}
                            </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
                  </Grid>

                  <Grid item xs={12} sm={2} sx={{ textAlign: 'center' }}>
                    <Tooltip title="Swap languages">
                      <IconButton 
                        onClick={handleSwapLanguages}
                        disabled={sourceLang === 'auto'}
                        sx={{ 
                          bgcolor: 'background.paper',
                          boxShadow: 1,
                          '&:hover': { boxShadow: 2 }
                        }}
                      >
                <SwapHorizIcon />
              </IconButton>
                    </Tooltip>
                  </Grid>

                  <Grid item xs={12} sm={5}>
                    <FormControl fullWidth>
                <InputLabel>To</InputLabel>
                <Select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  label="To"
                >
                  {languages.map((lang) => (
                    <MenuItem key={lang.code} value={lang.code}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography>{lang.native_name || lang.name}</Typography>
                              {lang.tts_supported && <VolumeUpIcon fontSize="small" color="action" />}
                            </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
                  </Grid>
                </Grid>

                {/* Advanced Options */}
                <Collapse in={showAdvanced}>
                  <Box sx={{ mt: 2 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={4}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Formality</InputLabel>
                          <Select
                            value={formality}
                            onChange={(e) => handleSettingsChange('formality', e.target.value)}
                            label="Formality"
                          >
                            {formalityLevels.map((level) => (
                              <MenuItem key={level.value} value={level.value}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <span>{level.icon}</span>
                                  <Box>
                                    <Typography variant="body2">{level.label}</Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      {level.description}
              </Typography>
                                  </Box>
                                </Box>
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>

                      {dialects[sourceLang] && (
                        <Grid item xs={12} sm={4}>
                          <FormControl fullWidth size="small">
                            <InputLabel>Dialect</InputLabel>
                            <Select
                              value={dialect}
                              onChange={(e) => handleSettingsChange('dialect', e.target.value)}
                              label="Dialect"
                            >
                              <MenuItem value="">Default</MenuItem>
                              {dialects[sourceLang].map((d) => (
                                <MenuItem key={d.value} value={d.value}>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <span>{d.flag}</span>
                                    {d.label}
                                  </Box>
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        </Grid>
                      )}

                      <Grid item xs={12} sm={4}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Voice</InputLabel>
                          <Select
                            value={voiceGender}
                            onChange={(e) => handleSettingsChange('voiceGender', e.target.value)}
                            label="Voice"
                          >
                            {voiceOptions.map((voice) => (
                              <MenuItem key={voice.value} value={voice.value}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <span>{voice.icon}</span>
                                  {voice.label}
                                </Box>
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                    </Grid>
                  </Box>
                </Collapse>

                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Button
                    startIcon={<TuneIcon />}
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    size="small"
                  >
                    {showAdvanced ? 'Hide' : 'Show'} Options
                  </Button>
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="History">
                      <IconButton onClick={() => setShowHistory(true)} size="small">
                        <Badge badgeContent={history.length > 0 ? history.length : null} color="primary">
                          <HistoryIcon />
                        </Badge>
                      </IconButton>
                    </Tooltip>
                    
                    <Tooltip title="Settings">
                      <IconButton onClick={() => setShowSettings(true)} size="small">
                        <SettingsIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Input/Output Section */}
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card elevation={2} sx={{ height: '100%' }}>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        {getLanguageName(sourceLang)} Text
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        {inputText && (
                          <Tooltip title="Copy">
                            <IconButton size="small" onClick={() => handleCopyText(inputText)}>
                <ContentCopyIcon fontSize="small" />
              </IconButton>
                          </Tooltip>
                        )}
                        {speechSupported && (
                          <Tooltip title={isRecording ? "Stop recording" : "Start recording"}>
                            <IconButton
                              size="small"
                              color={isRecording ? 'error' : 'primary'}
                              onClick={toggleRecording}
                            >
                              {isRecording ? <StopIcon /> : <MicIcon />}
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
            </Stack>

                    <TextField
                      multiline
                      rows={6}
                      fullWidth
                      value={inputText}
                      onChange={handleTextChange}
                      placeholder={isRecording ? "Listening..." : "Type or speak your text..."}
                      variant="outlined"
                      disabled={isRecording}
                      sx={getTextStyle(inputText, sourceLang)}
                      inputProps={{ maxLength: characterLimit }}
                    />

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {characterCount}/{characterLimit} characters
            </Typography>
                      
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleTranslate(false)}
                          disabled={!inputText.trim() || isTranslating}
                          startIcon={isTranslating ? <CircularProgress size={16} /> : <TranslateIcon />}
                        >
                          Translate
                        </Button>
                        
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleTranslate(true)}
                          disabled={!inputText.trim() || isTranslating}
                          startIcon={<InfoIcon />}
                        >
                          Advanced
                        </Button>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card elevation={2} sx={{ height: '100%' }}>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6">
                        {getLanguageName(targetLang)} Translation
              </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        {translatedText && (
                          <>
                            <Tooltip title="Copy translation">
                <IconButton size="small" onClick={() => handleCopyText(translatedText)}>
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
                            </Tooltip>
                            <Tooltip title="Play audio">
                              <IconButton size="small" onClick={() => playTranslatedAudio(translatedText)}>
                                <VolumeUpIcon fontSize="small" />
                  </IconButton>
                            </Tooltip>
                            <Tooltip title="Save as flashcard">
                              <IconButton size="small" onClick={saveAsFlashcard}>
                                <BookmarkIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                      </Box>
              </Stack>

                    <Box
                      sx={{
                        minHeight: 144,
                        p: 2,
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 1,
                        bgcolor: 'grey.50',
                        ...getTextStyle(translatedText, targetLang)
                      }}
                    >
                      <Typography variant="body1" color={translatedText ? 'text.primary' : 'text.secondary'}>
                        {translatedText || 'Translation will appear here...'}
                      </Typography>
                      
                      {/* Display romanization if available */}
                      {romanizationData && romanizationData.romanization && (
                        <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="body2" color="text.secondary">
                              Romanization:
                            </Typography>
                            <Tooltip title="Copy romanization">
                              <IconButton 
                                size="small" 
                                onClick={() => handleCopyText(romanizationData.romanization)}
                              >
                                <ContentCopyIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                          <Typography variant="body1" color="text.primary" sx={{ fontStyle: 'italic' }}>
                            {romanizationData.romanization}
                          </Typography>
                          {romanizationData.romanization_system && (
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                              System: {romanizationData.romanization_system}
                            </Typography>
                          )}
                        </Box>
                      )}
                    </Box>

                    {translation && (
                      <Box sx={{ mt: 2 }}>
                        <Button
                          size="small"
                          onClick={() => setShowAdvanced(true)}
                          startIcon={<InfoIcon />}
                        >
                          View Details
                        </Button>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            </Stack>
        )}

        {/* Conversation View */}
        {activeView === 'conversation' && (
          <Stack spacing={3}>
            <Card elevation={2}>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">
                    Conversation Mode
            </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      size="small"
                      onClick={() => setShowConversations(true)}
                      startIcon={<ForumIcon />}
                    >
                      History
                    </Button>
                    <Button
                      size="small"
                      onClick={startNewConversation}
                      startIcon={<ChatIcon />}
                      disabled={conversation.length === 0}
                    >
                      New
                    </Button>
                  </Box>
                </Stack>

                <Box sx={{ maxHeight: 400, overflow: 'auto', mb: 2 }}>
                  {conversation.length === 0 ? (
                    <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                      Start a conversation by typing a message
              </Typography>
                  ) : (
                    conversation.map((message) => (
                      <MessageBubble key={message.id} message={message} />
                    ))
            )}
                </Box>

                <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                multiline
                    maxRows={3}
                value={inputText}
                    onChange={handleTextChange}
                    placeholder="Type your message..."
                variant="outlined"
                size="small"
                  />
                  <Button
                    variant="contained"
                    onClick={() => {
                      setIsConversationMode(true);
                      handleTranslate();
                    }}
                    disabled={!inputText.trim() || isTranslating}
                    sx={{ minWidth: 'auto', px: 2 }}
                >
                  <SendIcon />
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Stack>
        )}

        {/* Learning View */}
        {activeView === 'learning' && (
          <LearningTools userId={userId} language={targetLang} />
        )}
      </Box>

      {/* Advanced Translation Dialog */}
      <Dialog
        open={showAdvanced && translation}
        onClose={() => setShowAdvanced(false)}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            Advanced Translation Analysis
            <IconButton onClick={() => setShowAdvanced(false)}>
              <DeleteIcon />
                </IconButton>
              </Stack>
        </DialogTitle>
        <DialogContent>
          {translation && (
            <AdvancedTranslation 
              translation={translation} 
              onSaveFlashcard={saveAsFlashcard}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* History Dialog */}
      <Dialog
        open={showHistory}
        onClose={() => setShowHistory(false)}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            Translation History
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button size="small" onClick={clearAllHistory} disabled={history.length === 0}>
                Clear All
              </Button>
              <IconButton onClick={() => setShowHistory(false)}>
                <DeleteIcon />
              </IconButton>
            </Box>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <List>
            {history.length === 0 ? (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No translation history yet
              </Typography>
            ) : (
              history.map((entry) => (
                <ListItem key={entry.id} divider>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body1">{entry.original}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {format(new Date(entry.timestamp), 'MMM dd, HH:mm')}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {entry.translated}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                          <Chip 
                            label={getLanguageName(entry.sourceLang)} 
                            size="small" 
                            variant="outlined" 
                          />
                          <SwapHorizIcon fontSize="small" color="action" />
                          <Chip 
                            label={getLanguageName(entry.targetLang)} 
                            size="small" 
                            variant="outlined" 
                          />
                          {entry.advanced && (
                            <Chip label="Advanced" size="small" color="primary" />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Use this translation">
                        <IconButton size="small" onClick={() => handleHistoryItemClick(entry)}>
                          <TranslateIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={favorites.some(f => f.id === entry.id) ? "Remove from favorites" : "Add to favorites"}>
                        <IconButton size="small" onClick={() => toggleFavorite(entry)}>
                          {favorites.some(f => f.id === entry.id) ? 
                            <StarIcon fontSize="small" color="primary" /> : 
                            <StarBorderIcon fontSize="small" />
                          }
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" onClick={() => deleteHistoryEntry(entry.id)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))
            )}
          </List>
        </DialogContent>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog
        open={showSettings}
        onClose={() => setShowSettings(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Settings</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Box>
              <Typography variant="subtitle1" gutterBottom>Speech Speed</Typography>
              <Slider
                value={speechSpeed}
                onChange={(e, value) => handleSettingsChange('speechSpeed', value)}
                min={0.5}
                max={2.0}
                step={0.1}
                marks={[
                  { value: 0.5, label: '0.5x' },
                  { value: 1.0, label: '1x' },
                  { value: 2.0, label: '2x' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <FormControlLabel
              control={
                <Switch
                  checked={autoPlayTranslations}
                  onChange={(e) => handleSettingsChange('autoPlayTranslations', e.target.checked)}
                />
              }
              label="Auto-play translations"
            />

            <Box>
              <Typography variant="subtitle1" gutterBottom>Default Languages</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>From</InputLabel>
                    <Select
                      value={sourceLang}
                      onChange={(e) => {
                        setSourceLang(e.target.value);
                        saveUserPreferences({ default_source_lang: e.target.value });
                      }}
                      label="From"
                    >
                      {languages.map((lang) => (
                        <MenuItem key={lang.code} value={lang.code}>
                          {lang.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>To</InputLabel>
                    <Select
                      value={targetLang}
                      onChange={(e) => {
                        setTargetLang(e.target.value);
                        saveUserPreferences({ default_target_lang: e.target.value });
                      }}
                      label="To"
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
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Conversations Dialog */}
      <Dialog
        open={showConversations}
        onClose={() => setShowConversations(false)}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
      >
        <DialogTitle>Saved Conversations</DialogTitle>
        <DialogContent>
          <List>
            {conversations.length === 0 ? (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No saved conversations yet
              </Typography>
            ) : (
              conversations.map((conv) => (
                <ListItem key={conv.id} divider>
                  <ListItemIcon>
                    <ChatIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={conv.title || `Conversation ${format(new Date(conv.timestamp), 'MMM dd, HH:mm')}`}
                    secondary={`${conv.messages.length} messages • ${conv.languages?.join(' ↔ ')}`}
                  />
                  <ListItemSecondaryAction>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="Load conversation">
                        <IconButton size="small" onClick={() => loadConversation(conv)}>
                          <TranslateIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" onClick={() => deleteConversation(conv.id)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))
            )}
          </List>
        </DialogContent>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={() => setNotification({ ...notification, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setNotification({ ...notification, open: false })} 
          severity={notification.severity}
          variant="filled"
        >
          {notification.message}
        </Alert>
      </Snackbar>

      {/* Error Display */}
      {error && (
        <Alert 
          severity="error" 
          onClose={() => setError(null)}
          sx={{ mt: 2 }}
        >
          {error}
        </Alert>
      )}

      {/* Floating Action Button for Mobile */}
      {isMobile && (
        <SpeedDial
          ariaLabel="Quick Actions"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          icon={<SpeedDialIcon />}
        >
          <SpeedDialAction
            icon={<MicIcon />}
            tooltipTitle="Voice Input"
            onClick={toggleRecording}
          />
          <SpeedDialAction
            icon={<HistoryIcon />}
            tooltipTitle="History"
            onClick={() => setShowHistory(true)}
          />
          <SpeedDialAction
            icon={<SettingsIcon />}
            tooltipTitle="Settings"
            onClick={() => setShowSettings(true)}
          />
        </SpeedDial>
      )}
    </Container>
  );
};

export default Translator; 