import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  CircularProgress,
  Alert,
  Snackbar,
  Divider,
  Chip,
  Stack,
  Tooltip,
  Paper,
  Grid
} from '@mui/material';
import {
  VolumeUp as VolumeUpIcon,
  BookmarkAdd as BookmarkAddIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Casino as CasinoIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import axios from 'axios';
import '../../styles/gradients.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const WordExplorer = ({ userId, language, onNotification }) => {
  // State management
  const [currentWord, setCurrentWord] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });
  
  // Filter and search state
  const [filterLanguage, setFilterLanguage] = useState(language || '');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearchMode, setIsSearchMode] = useState(false);

  // Difficulty and category options
  const difficultyOptions = [
    { value: 'all', label: 'All Levels' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' }
  ];

  const categoryOptions = [
    { value: 'all', label: 'All Categories' },
    { value: 'greetings', label: 'Greetings' },
    { value: 'travel', label: 'Travel' },
    { value: 'food', label: 'Food & Dining' },
    { value: 'business', label: 'Business' },
    { value: 'family', label: 'Family' },
    { value: 'emotions', label: 'Emotions' },
    { value: 'time', label: 'Time & Dates' },
    { value: 'general', label: 'General' }
  ];

  // Update filter language when prop changes
  useEffect(() => {
    if (language && language !== filterLanguage) {
      setFilterLanguage(language);
    }
  }, [language]);

  // Fetch initial word on component mount and filter changes
  useEffect(() => {
    if (filterLanguage && filterLanguage.trim() !== '') {
      fetchWord();
    }
  }, [filterLanguage]);

  const showNotification = useCallback((message, severity = 'info') => {
    setNotification({ open: true, message, severity });
    if (onNotification) {
      onNotification(message, severity);
    }
  }, [onNotification]);

  const fetchWord = async (forceSearch = false) => {
    if (!filterLanguage || filterLanguage.trim() === '') {
      showNotification('Please select a language', 'warning');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const params = {
        language: filterLanguage
      };

      // Add filters only if they're not 'all'
      if (filterDifficulty !== 'all') {
        params.difficulty = filterDifficulty;
      }
      if (filterCategory !== 'all') {
        params.category = filterCategory;
      }
      
      // Add search term if in search mode or force search
      if ((isSearchMode && searchTerm.trim()) || forceSearch) {
        params.searchTerm = searchTerm.trim();
      }

      const response = await axios.get(`${API_URL}/word-explorer/get-word`, { params });
      
      if (response.data) {
        setCurrentWord(response.data);
        if (forceSearch && searchTerm.trim()) {
          showNotification(`Found word: "${response.data.word}"`, 'success');
        }
      } else {
        setCurrentWord(null);
        showNotification('No words found matching your criteria', 'info');
      }
    } catch (err) {
      console.error('Error fetching word:', err);
      const errorMessage = err.response?.data?.error || 'Failed to fetch word';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (!searchTerm.trim()) {
      showNotification('Please enter a search term', 'warning');
      return;
    }
    setIsSearchMode(true);
    fetchWord(true);
  };

  const handleRandomWord = () => {
    setIsSearchMode(false);
    setSearchTerm('');
    fetchWord();
  };

  const handleAddToFlashcards = async () => {
    if (!currentWord) {
      showNotification('No word to save', 'warning');
      return;
    }

    try {
      const flashcardData = {
        translation: {
          originalText: currentWord.word,
          translatedText: currentWord.translation,
          sourceLang: filterLanguage,
          targetLang: 'en' // TODO: Make this configurable
        },
        difficulty: currentWord.difficulty || 'beginner',
        category: 'general',
        notes: `${currentWord.part_of_speech ? `Part of speech: ${currentWord.part_of_speech}. ` : ''}${currentWord.etymology ? `Etymology: ${currentWord.etymology}` : ''}`
      };

      const response = await axios.post(`${API_URL}/flashcards`, {
        userId,
        flashcard: flashcardData
      });

      if (response.data.success) {
        showNotification('Word saved as flashcard!', 'success');
      } else {
        showNotification('Failed to save flashcard', 'error');
      }
    } catch (err) {
      console.error('Error saving flashcard:', err);
      showNotification('Failed to save flashcard', 'error');
    }
  };

  const playAudio = async (text) => {
    if (!text) return;

    try {
      const response = await axios.post(`${API_URL}/text-to-speech`, {
        text,
        languageCode: filterLanguage,
        voiceGender: 'NEUTRAL',
        speed: 1.0
      });

      if (response.data.audio_content) {
        const audio = new Audio(`data:audio/mp3;base64,${response.data.audio_content}`);
        await audio.play();
        showNotification('Playing pronunciation', 'info');
      }
    } catch (err) {
      console.error('Error playing audio:', err);
      showNotification('Audio playback failed', 'error');
    }
  };

  return (
    <Box sx={{ maxWidth: '1000px', mx: 'auto' }}>
      {/* Main Card */}
      <Card className="card-gradient shadow-modern rounded-modern">
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Typography variant="h4" className="text-gradient" align="center" gutterBottom>
            Word Explorer
          </Typography>
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
            Discover new words with detailed explanations, pronunciation, and cultural context
          </Typography>

          {/* Filters and Search */}
          <Paper elevation={1} sx={{ p: 3, mb: 4, bgcolor: 'grey.50' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Difficulty</InputLabel>
                  <Select
                    value={filterDifficulty}
                    onChange={(e) => setFilterDifficulty(e.target.value)}
                    label="Difficulty"
                  >
                    {difficultyOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={filterCategory}
                    onChange={(e) => setFilterCategory(e.target.value)}
                    label="Category"
                  >
                    {categoryOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={8} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Search for a specific word..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  InputProps={{
                    endAdornment: (
                      <IconButton size="small" onClick={handleSearch} disabled={!searchTerm.trim()}>
                        <SearchIcon />
                      </IconButton>
                    )
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={4} md={2}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={handleRandomWord}
                  startIcon={<CasinoIcon />}
                  disabled={loading}
                >
                  Random
                </Button>
              </Grid>
            </Grid>
          </Paper>

          {/* Loading State */}
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {/* Word Display */}
          {!loading && currentWord && (
            <Box className="animate-fade-in">
              {/* Main Word */}
              <Paper elevation={2} sx={{ p: 4, mb: 3, textAlign: 'center', bgcolor: 'background.paper' }}>
                <Typography variant="h3" className="text-gradient" gutterBottom sx={{ fontWeight: 'bold' }}>
                  {currentWord.word}
                </Typography>
                
                {/* Pronunciation */}
                {currentWord.pronunciation && (
                  <Typography variant="h6" color="text.secondary" sx={{ fontFamily: 'monospace', mb: 2 }}>
                    [{currentWord.pronunciation}]
                  </Typography>
                )}

                {/* Translation */}
                <Typography variant="h5" color="primary" gutterBottom sx={{ fontWeight: '600' }}>
                  {currentWord.translation}
                </Typography>

                {/* Romanization Display */}
                {currentWord.romanization && (
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Romanization:
                    </Typography>
                    <Typography variant="h6" sx={{ fontStyle: 'italic', fontFamily: 'serif' }}>
                      {currentWord.romanization}
                    </Typography>
                    {currentWord.romanization_system && (
                      <Typography variant="caption" color="text.secondary">
                        System: {currentWord.romanization_system}
                      </Typography>
                    )}
                  </Box>
                )}

                {/* Action Buttons */}
                <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 3 }}>
                  <Tooltip title="Listen to pronunciation">
                    <IconButton 
                      className="button-gradient" 
                      onClick={() => playAudio(currentWord.word)}
                      sx={{ color: 'white' }}
                    >
                      <VolumeUpIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Add to flashcards">
                    <IconButton 
                      className="button-gradient" 
                      onClick={handleAddToFlashcards}
                      sx={{ color: 'white' }}
                    >
                      <BookmarkAddIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Get another word">
                    <IconButton 
                      className="button-gradient" 
                      onClick={handleRandomWord}
                      sx={{ color: 'white' }}
                    >
                      <RefreshIcon />
                    </IconButton>
                  </Tooltip>
                </Stack>
              </Paper>

              {/* Word Details */}
              <Grid container spacing={3}>
                {/* Left Column - Basic Info */}
                <Grid item xs={12} md={6}>
                  <Stack spacing={2}>
                    {/* Part of Speech & Difficulty */}
                    <Paper elevation={1} sx={{ p: 3 }}>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <InfoIcon color="primary" />
                        Word Information
                      </Typography>
                      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
                        {currentWord.part_of_speech && (
                          <Chip 
                            label={currentWord.part_of_speech} 
                            color="primary" 
                            variant="outlined" 
                            size="small" 
                          />
                        )}
                        {currentWord.difficulty && (
                          <Chip 
                            label={currentWord.difficulty} 
                            color="secondary" 
                            variant="outlined" 
                            size="small" 
                          />
                        )}
                      </Stack>
                      
                      {/* Etymology */}
                      {currentWord.etymology && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Etymology:
                          </Typography>
                          <Typography variant="body2">
                            {currentWord.etymology}
                          </Typography>
                        </Box>
                      )}

                      {/* Related Words */}
                      {currentWord.related_words && currentWord.related_words.length > 0 && (
                        <Box>
                          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                            Related Words:
                          </Typography>
                          <Stack direction="row" spacing={1} flexWrap="wrap">
                            {currentWord.related_words.map((word, index) => (
                              <Chip
                                key={index}
                                label={word}
                                size="small"
                                variant="outlined"
                                onClick={() => {
                                  setSearchTerm(word);
                                  setIsSearchMode(true);
                                  setTimeout(() => fetchWord(true), 100);
                                }}
                                sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'primary.light' } }}
                              />
                            ))}
                          </Stack>
                        </Box>
                      )}
                    </Paper>
                  </Stack>
                </Grid>

                {/* Right Column - Examples & Cultural Notes */}
                <Grid item xs={12} md={6}>
                  <Stack spacing={2}>
                    {/* Example Sentences */}
                    {currentWord.example_sentence && (
                      <Paper elevation={1} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          Example Usage
                        </Typography>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1, mb: 2 }}>
                          <Typography variant="body1" sx={{ fontStyle: 'italic', mb: 1 }}>
                            "{currentWord.example_sentence}"
                          </Typography>
                          {currentWord.example_translation && (
                            <Typography variant="body2" color="text.secondary">
                              {currentWord.example_translation}
                            </Typography>
                          )}
                        </Box>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<VolumeUpIcon />}
                          onClick={() => playAudio(currentWord.example_sentence)}
                        >
                          Listen to Example
                        </Button>
                      </Paper>
                    )}

                    {/* Cultural Notes */}
                    {currentWord.cultural_note && (
                      <Paper elevation={1} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          Cultural Context
                        </Typography>
                        <Alert severity="info" sx={{ bgcolor: 'transparent', border: '1px solid', borderColor: 'info.main' }}>
                          {currentWord.cultural_note}
                        </Alert>
                      </Paper>
                    )}
                  </Stack>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* No Word State */}
          {!loading && !currentWord && (
            <Box sx={{ textAlign: 'center', py: 6 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No word to display
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Try adjusting your filters or search for a specific word
              </Typography>
              <Button 
                variant="contained" 
                onClick={handleRandomWord}
                startIcon={<CasinoIcon />}
                className="button-gradient"
              >
                Get Random Word
              </Button>
            </Box>
          )}

          {/* Error Display */}
          {error && (
            <Alert 
              severity="error" 
              onClose={() => setError('')}
              sx={{ mt: 2 }}
            >
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

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
    </Box>
  );
};

export default WordExplorer;