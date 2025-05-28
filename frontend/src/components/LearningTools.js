import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  IconButton,
  Grid,
  CircularProgress,
  Snackbar,
  Alert,
  Paper,
  Stack,
  Chip,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  School as SchoolIcon,
  FlashOn as FlashOnIcon,
  Quiz as QuizIcon,
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  Check as CheckIcon,
  VolumeUp as VolumeUpIcon,
  Refresh as RefreshIcon,
  EmojiEvents as EmojiEventsIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const LearningTools = ({ userId, language }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [flashcards, setFlashcards] = useState([]);
  const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [wordOfDay, setWordOfDay] = useState(null);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    if (language) {
      fetchWordOfDay();
      fetchFlashcards();
      fetchProgress();
    }
  }, [language]);

  const fetchWordOfDay = async () => {
    try {
      const response = await axios.get(`${API_URL}/word-of-day`, {
        params: { language }
      });
      setWordOfDay(response.data);
    } catch (err) {
      console.error('Error fetching word of day:', err);
      setError('Failed to fetch word of the day');
    }
  };

  const fetchFlashcards = async () => {
    try {
      const response = await axios.get(`${API_URL}/flashcards`, {
        params: { userId, language }
      });
      setFlashcards(response.data);
    } catch (err) {
      console.error('Error fetching flashcards:', err);
      setError('Failed to fetch flashcards');
    }
  };

  const fetchProgress = async () => {
    try {
      const response = await axios.get(`${API_URL}/progress`, {
        params: { userId, language }
      });
      setProgress(response.data);
    } catch (err) {
      console.error('Error fetching progress:', err);
    }
  };

  const startNewQuiz = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/quiz/generate`, {
        userId,
        language,
        difficulty: 'beginner'
      });
      setQuiz(response.data.questions);
    } catch (err) {
      console.error('Error starting quiz:', err);
      setError('Failed to start quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleFlashcardNavigation = (direction) => {
    setShowAnswer(false);
    if (direction === 'next') {
      setCurrentFlashcardIndex((prev) => 
        prev === flashcards.length - 1 ? 0 : prev + 1
      );
    } else {
      setCurrentFlashcardIndex((prev) => 
        prev === 0 ? flashcards.length - 1 : prev - 1
      );
    }
  };

  const handleQuizSubmit = async () => {
    if (!selectedAnswer) return;
    
    try {
      const response = await axios.post(`${API_URL}/quiz/submit`, {
        userId,
        questionId: quiz[0].id,
        answer: selectedAnswer
      });
      
      setNotification({
        open: true,
        message: response.data.correct ? 'Correct!' : 'Incorrect. Try again!',
        severity: response.data.correct ? 'success' : 'error'
      });
      
      if (response.data.correct) {
        setQuiz(prev => prev.slice(1));
        setSelectedAnswer('');
      }
    } catch (err) {
      setError('Failed to submit answer');
    }
  };

  const playAudio = async (text) => {
    try {
      const response = await axios.post(`${API_URL}/text-to-speech`, {
        text,
        languageCode: language
      });
      const audio = new Audio(`data:audio/mp3;base64,${response.data.audioContent}`);
      audio.play();
    } catch (err) {
      console.error('Error playing audio:', err);
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto' }}>
      <Tabs 
        value={activeTab} 
        onChange={(e, newValue) => setActiveTab(newValue)}
        variant="fullWidth"
        sx={{ mb: 3 }}
      >
        <Tab icon={<FlashOnIcon />} label="Practice" />
        <Tab icon={<QuizIcon />} label="Quiz" />
        <Tab icon={<TimelineIcon />} label="Progress" />
      </Tabs>

      {/* Practice Tab */}
      {activeTab === 0 && (
        <Stack spacing={3}>
          {/* Word of the Day Card */}
          <Card elevation={3}>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                <SchoolIcon color="primary" />
                <Typography variant="h6">Word of the Day</Typography>
              </Stack>
              {wordOfDay ? (
                <Box
                  sx={{
                    textAlign: 'center',
                    py: 3,
                  }}
                >
                  <Typography variant="h4" color="primary" gutterBottom>
                    {wordOfDay.word}
                  </Typography>
                  <IconButton 
                    onClick={() => playAudio(wordOfDay.word)}
                    sx={{ mb: 2 }}
                  >
                    <VolumeUpIcon />
                  </IconButton>
                  <Typography variant="h6" gutterBottom>
                    {wordOfDay.translation}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {wordOfDay.pronunciation}
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="body1" sx={{ fontStyle: 'italic', mb: 2 }}>
                    "{wordOfDay.example}"
                  </Typography>
                  <Stack direction="row" spacing={1} justifyContent="center">
                    <Chip 
                      label={wordOfDay.part_of_speech} 
                      color="primary" 
                      variant="outlined" 
                      size="small" 
                    />
                    <Chip 
                      label={wordOfDay.difficulty} 
                      color="secondary" 
                      variant="outlined" 
                      size="small" 
                    />
                  </Stack>
                </Box>
              ) : (
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Flashcards */}
          {flashcards.length > 0 && (
            <Card elevation={3}>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                  <FlashOnIcon color="primary" />
                  <Typography variant="h6">Flashcards</Typography>
                </Stack>
                <Box
                  onClick={() => setShowAnswer(!showAnswer)}
                  sx={{
                    minHeight: 200,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    bgcolor: 'background.paper',
                    borderRadius: 1,
                    p: 4,
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.02)',
                    },
                  }}
                >
                  <Typography variant="h4" align="center" gutterBottom>
                    {showAnswer 
                      ? flashcards[currentFlashcardIndex].translation.translatedText
                      : flashcards[currentFlashcardIndex].translation.originalText
                    }
                  </Typography>
                  {showAnswer && (
                    <IconButton 
                      onClick={(e) => {
                        e.stopPropagation();
                        playAudio(flashcards[currentFlashcardIndex].translation.translatedText);
                      }}
                      sx={{ mt: 2 }}
                    >
                      <VolumeUpIcon />
                    </IconButton>
                  )}
                </Box>
                <Stack 
                  direction="row" 
                  justifyContent="space-between" 
                  alignItems="center"
                  mt={2}
                >
                  <IconButton onClick={() => handleFlashcardNavigation('prev')}>
                    <ArrowBackIcon />
                  </IconButton>
                  <Typography>
                    {currentFlashcardIndex + 1} / {flashcards.length}
                  </Typography>
                  <IconButton onClick={() => handleFlashcardNavigation('next')}>
                    <ArrowForwardIcon />
                  </IconButton>
                </Stack>
              </CardContent>
            </Card>
          )}
        </Stack>
      )}

      {/* Quiz Tab */}
      {activeTab === 1 && (
        <Card elevation={3}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} mb={3}>
              <QuizIcon color="primary" />
              <Typography variant="h6">Language Quiz</Typography>
            </Stack>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : quiz && quiz.length > 0 ? (
              <Stack spacing={3}>
                <Typography variant="h5" align="center" gutterBottom>
                  {quiz[0].question}
                </Typography>
                <Grid container spacing={2}>
                  {quiz[0].options.map((option, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <Button
                        variant={selectedAnswer === option ? "contained" : "outlined"}
                        fullWidth
                        onClick={() => setSelectedAnswer(option)}
                        sx={{ 
                          py: 3,
                          typography: 'h6',
                        }}
                      >
                        {option}
                      </Button>
                    </Grid>
                  ))}
                </Grid>
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  disabled={!selectedAnswer}
                  onClick={handleQuizSubmit}
                  startIcon={<CheckIcon />}
                  sx={{ mt: 2 }}
                >
                  Submit Answer
                </Button>
              </Stack>
            ) : (
              <Stack spacing={2} alignItems="center" py={4}>
                <Typography variant="h6">Ready to test your knowledge?</Typography>
                <Button
                  variant="contained"
                  size="large"
                  onClick={startNewQuiz}
                  startIcon={<RefreshIcon />}
                >
                  Start New Quiz
                </Button>
              </Stack>
            )}
          </CardContent>
        </Card>
      )}

      {/* Progress Tab */}
      {activeTab === 2 && (
        <Card elevation={3}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} mb={3}>
              <EmojiEventsIcon color="primary" />
              <Typography variant="h6">Learning Progress</Typography>
            </Stack>
            {progress ? (
              <Stack spacing={4}>
                <Box>
                  <Typography variant="h5" gutterBottom align="center">
                    Level {progress.level}
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={(progress.xp % 100)} 
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                  <Typography variant="body2" color="text.secondary" align="right">
                    {progress.xp} XP
                  </Typography>
                </Box>

                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center',
                        bgcolor: 'primary.light',
                        color: 'primary.contrastText',
                      }}
                    >
                      <Typography variant="h6" gutterBottom>
                        Daily Streak
                      </Typography>
                      <Typography variant="h2">
                        {progress.streak}
                      </Typography>
                      <Typography variant="subtitle1">
                        days
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center',
                        bgcolor: 'secondary.light',
                        color: 'secondary.contrastText',
                      }}
                    >
                      <Typography variant="h6" gutterBottom>
                        Words Learned
                      </Typography>
                      <Typography variant="h2">
                        {progress.wordsLearned}
                      </Typography>
                      <Typography variant="subtitle1">
                        total
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Stack>
            ) : (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LearningTools; 