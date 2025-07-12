import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Chip,
  Stack,
  CircularProgress,
  Alert,
  Snackbar,
  Grid,
  Paper,
  LinearProgress,
  Tabs,
  Tab,
  Tooltip,
  Fab
} from '@mui/material';
import {
  AddCircleOutline as AddCircleOutlineIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayArrowIcon,
  FlipCameraIos as FlipCameraIosIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  VolumeUp as VolumeUpIcon,
  FilterList as FilterListIcon,
  Sort as SortIcon,
  Dashboard as DashboardIcon,
  Quiz as QuizIcon,
  ViewList as ViewListIcon,
  Add as AddIcon
} from '@mui/icons-material';
import axios from 'axios';
import '../../styles/gradients.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const FlashcardManager = ({ userId, language, onNotification }) => {
  // Main state
  const [flashcards, setFlashcards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState({ 
    open: false, 
    message: '', 
    severity: 'success' 
  });

  // View state
  const [activeView, setActiveView] = useState('dashboard'); // dashboard, review, browse
  const [currentReviewCardIndex, setCurrentReviewCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [reviewModeActive, setReviewModeActive] = useState(false);
  const [reviewCards, setReviewCards] = useState([]);

  // Dialog state
  const [showCreateEditDialog, setShowCreateEditDialog] = useState(false);
  const [editingCard, setEditingCard] = useState(null);

  // Filter and sort state
  const [filterLanguage, setFilterLanguage] = useState(language || '');
  const [filterDifficulty, setFilterDifficulty] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [sortOrder, setSortOrder] = useState('created_at_desc');

  // Form state for create/edit dialog
  const [formData, setFormData] = useState({
    originalText: '',
    translatedText: '',
    sourceLang: 'en',
    targetLang: language || 'es',
    difficulty: 'beginner',
    category: 'general',
    notes: ''
  });

  // Options
  const difficultyOptions = [
    { value: 'all', label: 'All Levels' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' }
  ];

  const categoryOptions = [
    { value: 'all', label: 'All Categories' },
    { value: 'general', label: 'General' },
    { value: 'greetings', label: 'Greetings' },
    { value: 'travel', label: 'Travel' },
    { value: 'food', label: 'Food & Dining' },
    { value: 'business', label: 'Business' },
    { value: 'family', label: 'Family' },
    { value: 'emotions', label: 'Emotions' },
    { value: 'time', label: 'Time & Dates' }
  ];

  const sortOptions = [
    { value: 'created_at_desc', label: 'Newest First' },
    { value: 'created_at_asc', label: 'Oldest First' },
    { value: 'next_review_asc', label: 'Review Due Soon' },
    { value: 'mastery_level_desc', label: 'Most Mastered' },
    { value: 'mastery_level_asc', label: 'Least Mastered' }
  ];

  // Update filter language when prop changes
  useEffect(() => {
    if (language && language !== filterLanguage) {
      setFilterLanguage(language);
      setFormData(prev => ({ ...prev, targetLang: language }));
    }
  }, [language]);

  // Fetch flashcards on component mount and filter changes
  useEffect(() => {
    if (filterLanguage && filterLanguage.trim() !== '') {
      fetchFlashcards();
    }
  }, [filterLanguage, filterDifficulty, filterCategory, sortOrder]);

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
    if (onNotification) {
      onNotification(message, severity);
    }
  };

  const fetchFlashcards = async () => {
    setLoading(true);
    setError('');

    try {
      const params = {
        userId,
        language: filterLanguage
      };

      // Add filters
      if (filterDifficulty !== 'all') {
        params.difficulty = filterDifficulty;
      }
      if (filterCategory !== 'all') {
        params.category = filterCategory;
      }

      const response = await axios.get(`${API_URL}/flashcards`, { params });
      
      let flashcardsData = response.data.flashcards || response.data || [];
      
      // Apply sorting
      flashcardsData = sortFlashcards(flashcardsData, sortOrder);
      
      setFlashcards(flashcardsData);
      
      // Update review cards (cards due for review)
      const now = new Date();
      const dueCards = flashcardsData.filter(card => 
        card.next_review && new Date(card.next_review) <= now
      );
      setReviewCards(dueCards);

    } catch (err) {
      console.error('Error fetching flashcards:', err);
      const errorMessage = err.response?.data?.error || 'Failed to fetch flashcards';
      setError(errorMessage);
      showNotification(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const sortFlashcards = (cards, order) => {
    const sorted = [...cards];
    
    switch (order) {
      case 'created_at_desc':
        return sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      case 'created_at_asc':
        return sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      case 'next_review_asc':
        return sorted.sort((a, b) => {
          if (!a.next_review) return 1;
          if (!b.next_review) return -1;
          return new Date(a.next_review) - new Date(b.next_review);
        });
      case 'mastery_level_desc':
        return sorted.sort((a, b) => b.mastery_level - a.mastery_level);
      case 'mastery_level_asc':
        return sorted.sort((a, b) => a.mastery_level - b.mastery_level);
      default:
        return sorted;
    }
  };

  const saveFlashcard = async () => {
    if (!formData.originalText.trim() || !formData.translatedText.trim()) {
      showNotification('Please fill in both original and translated text', 'warning');
      return;
    }

    try {
      const flashcardData = {
        id: editingCard?.id,
        translation: {
          originalText: formData.originalText.trim(),
          translatedText: formData.translatedText.trim(),
          sourceLang: formData.sourceLang,
          targetLang: formData.targetLang
        },
        difficulty: formData.difficulty,
        category: formData.category,
        notes: formData.notes
      };

      const response = await axios.post(`${API_URL}/flashcards`, {
        userId,
        flashcard: flashcardData
      });

      if (response.data.success) {
        showNotification(editingCard ? 'Flashcard updated!' : 'Flashcard created!', 'success');
        setShowCreateEditDialog(false);
        resetForm();
        fetchFlashcards();
      } else {
        showNotification('Failed to save flashcard', 'error');
      }
    } catch (err) {
      console.error('Error saving flashcard:', err);
      showNotification('Failed to save flashcard', 'error');
    }
  };

  const deleteFlashcard = async (flashcardId) => {
    if (!window.confirm('Are you sure you want to delete this flashcard?')) {
      return;
    }

    try {
      const response = await axios.delete(`${API_URL}/flashcards/${flashcardId}`, {
        params: { userId }
      });

      if (response.data.success) {
        showNotification('Flashcard deleted', 'success');
        fetchFlashcards();
      } else {
        showNotification('Failed to delete flashcard', 'error');
      }
    } catch (err) {
      console.error('Error deleting flashcard:', err);
      showNotification('Failed to delete flashcard', 'error');
    }
  };

  const reviewFlashcard = async (flashcardId, correct) => {
    try {
      const response = await axios.post(`${API_URL}/flashcards/${flashcardId}/review`, {
        userId,
        correct,
        timeTaken: 0 // TODO: Implement actual time tracking
      });

      if (response.data.success) {
        showNotification(correct ? 'Marked as correct!' : 'Marked as incorrect', 'info');
        
        // Move to next card or finish review
        if (currentReviewCardIndex < reviewCards.length - 1) {
          setCurrentReviewCardIndex(prev => prev + 1);
          setShowAnswer(false);
        } else {
          // Review session complete
          setReviewModeActive(false);
          setActiveView('dashboard');
          showNotification(`Review session complete! Reviewed ${reviewCards.length} cards.`, 'success');
        }
        
        fetchFlashcards(); // Refresh to update stats
      }
    } catch (err) {
      console.error('Error reviewing flashcard:', err);
      showNotification('Failed to record review', 'error');
    }
  };

  const playAudio = async (text, langCode = filterLanguage) => {
    try {
      const response = await axios.post(`${API_URL}/text-to-speech`, {
        text,
        languageCode: langCode,
        voiceGender: 'NEUTRAL',
        speed: 1.0
      });

      if (response.data.audio_content) {
        const audio = new Audio(`data:audio/mp3;base64,${response.data.audio_content}`);
        await audio.play();
      }
    } catch (err) {
      console.error('Error playing audio:', err);
      showNotification('Audio playback failed', 'error');
    }
  };

  const startReview = () => {
    if (reviewCards.length === 0) {
      showNotification('No cards due for review', 'info');
      return;
    }
    setActiveView('review');
    setReviewModeActive(true);
    setCurrentReviewCardIndex(0);
    setShowAnswer(false);
  };

  const openCreateDialog = () => {
    setEditingCard(null);
    resetForm();
    setShowCreateEditDialog(true);
  };

  const openEditDialog = (card) => {
    setEditingCard(card);
    setFormData({
      originalText: card.translation?.originalText || card.original_text || '',
      translatedText: card.translation?.translatedText || card.translated_text || '',
      sourceLang: card.translation?.sourceLang || card.source_lang || 'en',
      targetLang: card.translation?.targetLang || card.target_lang || filterLanguage,
      difficulty: card.difficulty || 'beginner',
      category: card.category || 'general',
      notes: card.notes || ''
    });
    setShowCreateEditDialog(true);
  };

  const resetForm = () => {
    setFormData({
      originalText: '',
      translatedText: '',
      sourceLang: 'en',
      targetLang: filterLanguage,
      difficulty: 'beginner',
      category: 'general',
      notes: ''
    });
    setEditingCard(null);
  };

  // Calculate stats for dashboard
  const stats = {
    total: flashcards.length,
    dueForReview: reviewCards.length,
    mastered: flashcards.filter(card => card.mastery_level >= 5).length,
    avgSuccessRate: flashcards.length > 0 
      ? flashcards.reduce((sum, card) => sum + (card.success_rate || 0), 0) / flashcards.length 
      : 0
  };

  // Dashboard View
  const renderDashboard = () => (
    <Box>
      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={6} md={3}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h4" className="text-gradient" fontWeight="bold">
              {stats.total}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Cards
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h4" className="text-gradient" fontWeight="bold">
              {stats.dueForReview}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Due for Review
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h4" className="text-gradient" fontWeight="bold">
              {stats.mastered}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Mastered
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h4" className="text-gradient" fontWeight="bold">
              {Math.round(stats.avgSuccessRate * 100)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Success Rate
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Button
            fullWidth
            variant="contained"
            size="large"
            className="button-gradient"
            startIcon={<PlayArrowIcon />}
            onClick={startReview}
            disabled={stats.dueForReview === 0}
          >
            Start Review ({stats.dueForReview})
          </Button>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Button
            fullWidth
            variant="outlined"
            size="large"
            startIcon={<AddCircleOutlineIcon />}
            onClick={openCreateDialog}
          >
            Create New Flashcard
          </Button>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Button
            fullWidth
            variant="outlined"
            size="large"
            startIcon={<ViewListIcon />}
            onClick={() => setActiveView('browse')}
          >
            Browse All Flashcards
          </Button>
        </Grid>
      </Grid>

      {/* Progress Visualization */}
      {stats.total > 0 && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Mastery Progress
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{ width: '100%', mr: 1 }}>
              <LinearProgress 
                variant="determinate" 
                value={(stats.mastered / stats.total) * 100} 
                className="progress-gradient"
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
            <Box sx={{ minWidth: 35 }}>
              <Typography variant="body2" color="text.secondary">
                {Math.round((stats.mastered / stats.total) * 100)}%
              </Typography>
            </Box>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {stats.mastered} of {stats.total} cards mastered
          </Typography>
        </Paper>
      )}
    </Box>
  );

  // Review Mode View
  const renderReview = () => {
    if (reviewCards.length === 0) {
      return (
        <Box textAlign="center" py={6}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No cards due for review
          </Typography>
          <Button onClick={() => setActiveView('dashboard')}>
            Back to Dashboard
          </Button>
        </Box>
      );
    }

    const currentCard = reviewCards[currentReviewCardIndex];
    if (!currentCard) return null;

    return (
      <Box>
        {/* Progress */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">
              Card {currentReviewCardIndex + 1} of {reviewCards.length}
            </Typography>
            <Typography variant="body2">
              Mastery Level: {currentCard.mastery_level}/5
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={(currentReviewCardIndex / reviewCards.length) * 100} 
            className="progress-gradient"
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>

        {/* Flashcard */}
        <Paper 
          elevation={3} 
          sx={{ 
            p: 4, 
            mb: 3, 
            minHeight: 200, 
            display: 'flex', 
            flexDirection: 'column', 
            justifyContent: 'center',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'transform 0.3s ease',
            '&:hover': { transform: 'scale(1.02)' }
          }}
          onClick={() => setShowAnswer(!showAnswer)}
        >
          <Typography variant="h4" gutterBottom>
            {showAnswer 
              ? currentCard.translation?.translatedText || currentCard.translated_text
              : currentCard.translation?.originalText || currentCard.original_text
            }
          </Typography>
          
          {showAnswer && (
            <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 2 }}>
              <IconButton 
                onClick={(e) => {
                  e.stopPropagation();
                  playAudio(currentCard.translation?.translatedText || currentCard.translated_text);
                }}
                className="button-gradient"
                sx={{ color: 'white' }}
              >
                <VolumeUpIcon />
              </IconButton>
            </Stack>
          )}
          
          {!showAnswer && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Click to reveal answer
            </Typography>
          )}
        </Paper>

        {/* Action Buttons */}
        {!showAnswer ? (
          <Button
            fullWidth
            variant="outlined"
            size="large"
            onClick={() => setShowAnswer(true)}
            startIcon={<FlipCameraIosIcon />}
          >
            Show Answer
          </Button>
        ) : (
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant="outlined"
                size="large"
                color="error"
                startIcon={<CancelIcon />}
                onClick={() => reviewFlashcard(currentCard.id, false)}
              >
                Incorrect
              </Button>
            </Grid>
            <Grid item xs={6}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                className="button-gradient"
                startIcon={<CheckCircleIcon />}
                onClick={() => reviewFlashcard(currentCard.id, true)}
              >
                Correct
              </Button>
            </Grid>
          </Grid>
        )}

        {/* Navigation */}
        <Stack direction="row" justifyContent="space-between" sx={{ mt: 3 }}>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={() => {
              if (currentReviewCardIndex > 0) {
                setCurrentReviewCardIndex(prev => prev - 1);
                setShowAnswer(false);
              }
            }}
            disabled={currentReviewCardIndex === 0}
          >
            Previous
          </Button>
          
          <Button
            variant="outlined"
            onClick={() => {
              setReviewModeActive(false);
              setActiveView('dashboard');
            }}
          >
            Exit Review
          </Button>
          
          <Button
            variant="outlined"
            endIcon={<ArrowForwardIcon />}
            onClick={() => {
              if (currentReviewCardIndex < reviewCards.length - 1) {
                setCurrentReviewCardIndex(prev => prev + 1);
                setShowAnswer(false);
              }
            }}
            disabled={currentReviewCardIndex === reviewCards.length - 1}
          >
            Next
          </Button>
        </Stack>
      </Box>
    );
  };

  // Browse/Manage View
  const renderBrowse = () => (
    <Box>
      {/* Filters */}
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
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
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value)}
                label="Sort By"
              >
                {sortOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<AddCircleOutlineIcon />}
              onClick={openCreateDialog}
            >
              Add New
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Flashcards List */}
      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : flashcards.length === 0 ? (
        <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No flashcards found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create your first flashcard to start learning!
          </Typography>
          <Button
            variant="contained"
            className="button-gradient"
            onClick={openCreateDialog}
          >
            Create Flashcard
          </Button>
        </Paper>
      ) : (
        <List>
          {flashcards.map((card, index) => (
            <React.Fragment key={card.id || index}>
              <ListItem sx={{ py: 2 }}>
                <ListItemText
                  primary={
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {card.translation?.originalText || card.original_text}
                      </Typography>
                      <Typography variant="body1" color="primary">
                        {card.translation?.translatedText || card.translated_text}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                      <Chip label={card.difficulty} size="small" variant="outlined" />
                      <Chip label={card.category} size="small" variant="outlined" />
                      <Chip 
                        label={`Level ${card.mastery_level}/5`} 
                        size="small" 
                        color={card.mastery_level >= 5 ? 'success' : 'default'}
                      />
                      {card.success_rate && (
                        <Chip 
                          label={`${Math.round(card.success_rate * 100)}% success`} 
                          size="small" 
                          variant="outlined"
                        />
                      )}
                    </Stack>
                  }
                />
                <ListItemSecondaryAction>
                  <Stack direction="row" spacing={1}>
                    <Tooltip title="Play audio">
                      <IconButton 
                        size="small" 
                        onClick={() => playAudio(card.translation?.translatedText || card.translated_text)}
                      >
                        <VolumeUpIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => openEditDialog(card)}>
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => deleteFlashcard(card.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </ListItemSecondaryAction>
              </ListItem>
              {index < flashcards.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      )}
    </Box>
  );

  return (
    <Box sx={{ maxWidth: '1000px', mx: 'auto' }}>
      {/* Main Card */}
      <Card className="card-gradient shadow-modern rounded-modern">
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Typography variant="h4" className="text-gradient" align="center" gutterBottom>
            Flashcard Manager
          </Typography>
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
            Review and manage your flashcards with spaced repetition system
          </Typography>

          {/* Language Check */}
          {(!filterLanguage || filterLanguage.trim() === '') ? (
            <Alert severity="warning" sx={{ mb: 3 }}>
              Please select a target language to manage your flashcards.
            </Alert>
          ) : (
            <>
              {/* Navigation Tabs */}
              <Tabs 
                value={activeView} 
                onChange={(e, newValue) => setActiveView(newValue)}
                variant="fullWidth"
                sx={{ mb: 3 }}
              >
                <Tab 
                  icon={<DashboardIcon />} 
                  label="Dashboard" 
                  value="dashboard"
                />
                <Tab 
                  icon={<QuizIcon />} 
                  label={`Review (${reviewCards.length})`}
                  value="review"
                />
                <Tab 
                  icon={<ViewListIcon />} 
                  label={`Browse (${flashcards.length})`}
                  value="browse"
                />
              </Tabs>

              {/* Content */}
              {activeView === 'dashboard' && renderDashboard()}
              {activeView === 'review' && renderReview()}
              {activeView === 'browse' && renderBrowse()}
            </>
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

      {/* Floating Action Button for Mobile */}
      <Fab
        color="primary"
        className="button-gradient"
        sx={{ 
          position: 'fixed', 
          bottom: 16, 
          right: 16,
          display: { xs: 'flex', sm: 'none' }
        }}
        onClick={openCreateDialog}
      >
        <AddIcon />
      </Fab>

      {/* Create/Edit Dialog */}
      <Dialog 
        open={showCreateEditDialog} 
        onClose={() => setShowCreateEditDialog(false)}
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle>
          {editingCard ? 'Edit Flashcard' : 'Create New Flashcard'}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              fullWidth
              label="Original Text"
              value={formData.originalText}
              onChange={(e) => setFormData(prev => ({ ...prev, originalText: e.target.value }))}
              placeholder="Enter the word or phrase"
              autoFocus
            />
            
            <TextField
              fullWidth
              label="Translation"
              value={formData.translatedText}
              onChange={(e) => setFormData(prev => ({ ...prev, translatedText: e.target.value }))}
              placeholder="Enter the translation"
            />
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Difficulty</InputLabel>
                  <Select
                    value={formData.difficulty}
                    onChange={(e) => setFormData(prev => ({ ...prev, difficulty: e.target.value }))}
                    label="Difficulty"
                  >
                    <MenuItem value="beginner">Beginner</MenuItem>
                    <MenuItem value="intermediate">Intermediate</MenuItem>
                    <MenuItem value="advanced">Advanced</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    label="Category"
                  >
                    {categoryOptions.slice(1).map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            
            <TextField
              fullWidth
              label="Notes (Optional)"
              value={formData.notes}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              placeholder="Add any notes or context"
              multiline
              rows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCreateEditDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={saveFlashcard}
            variant="contained"
            className="button-gradient"
          >
            {editingCard ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
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
    </Box>
  );
};

export default FlashcardManager;