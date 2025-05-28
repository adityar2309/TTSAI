import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  useMediaQuery,
  Paper,
  Grid,
  Radio,
  RadioGroup,
  FormControlLabel,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  School as SchoolIcon,
  FlashOn as FlashOnIcon,
  Quiz as QuizIcon,
  Translate as TranslateIcon,
  ArrowBack as ArrowBackIcon,
  ArrowForward as ArrowForwardIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Delete as DeleteIcon,
  Star as StarIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const LearningTools = ({ userId, language }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [flashcards, setFlashcards] = useState([]);
  const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [quizScore, setQuizScore] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [wordOfDay, setWordOfDay] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [quizAnswer, setQuizAnswer] = useState('');
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    if (language) {
      fetchWordOfDay();
      fetchFlashcards();
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

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    if (newValue === 1) { // Quiz tab
      startNewQuiz();
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

  const handleAnswerSelection = (answer) => {
    setSelectedAnswer(answer);
    const isCorrect = answer === quizQuestions[currentQuestionIndex].correct_answer;
    if (isCorrect) {
      setQuizScore((prev) => prev + 1);
    }

    // Move to next question or complete quiz
    setTimeout(() => {
      if (currentQuestionIndex < quizQuestions.length - 1) {
        setCurrentQuestionIndex((prev) => prev + 1);
        setSelectedAnswer(null);
      } else {
        setQuizCompleted(true);
      }
    }, 1000);
  };

  const handleQuizSubmit = async () => {
    if (!quizAnswer) return;
    
    try {
      const response = await axios.post(`${API_URL}/quiz/submit`, {
        userId,
        questionId: quiz[0].id,
        answer: quizAnswer
      });
      
      setNotification({
        open: true,
        message: response.data.correct ? 'Correct!' : 'Incorrect. Try again!',
        severity: response.data.correct ? 'success' : 'error'
      });
      
      if (response.data.correct) {
        setQuiz(prev => prev.slice(1));
        setQuizAnswer('');
      }
    } catch (err) {
      setError('Failed to submit answer');
    }
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto' }}>
      <Tabs 
        value={activeTab} 
        onChange={handleTabChange}
        variant={isMobile ? "scrollable" : "standard"}
        scrollButtons={isMobile ? "auto" : false}
        sx={{ mb: 3 }}
      >
        <Tab icon={<FlashOnIcon />} label="Flashcards" />
        <Tab icon={<QuizIcon />} label="Quiz" />
        <Tab icon={<SchoolIcon />} label="Daily Learning" />
      </Tabs>

      {/* Word of the Day */}
      {activeTab === 0 && (
        <Card 
          sx={{ 
            mb: 3,
            background: theme.palette.mode === 'dark' 
              ? 'rgba(255, 255, 255, 0.05)' 
              : 'rgba(0, 0, 0, 0.02)',
            backdropFilter: 'blur(10px)',
          }}
        >
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Word of the Day
            </Typography>
            {wordOfDay ? (
              <>
                <Typography variant="h5" color="primary" gutterBottom>
                  {wordOfDay.word}
                </Typography>
                <Typography variant="body1">
                  {wordOfDay.translation}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {wordOfDay.example}
                </Typography>
              </>
            ) : (
              <Typography>Loading word of the day...</Typography>
            )}
          </CardContent>
        </Card>
      )}

      {/* Flashcards */}
      {activeTab === 1 && flashcards.length > 0 && (
        <Card 
          sx={{ 
            minHeight: 300,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            background: theme.palette.mode === 'dark' 
              ? 'rgba(255, 255, 255, 0.05)' 
              : 'rgba(0, 0, 0, 0.02)',
            backdropFilter: 'blur(10px)',
          }}
        >
          <CardContent>
            <Box 
              sx={{ 
                minHeight: 200, 
                display: 'flex', 
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
              onClick={() => setShowAnswer(!showAnswer)}
            >
              <Typography variant="h5" gutterBottom>
                {showAnswer 
                  ? flashcards[currentFlashcardIndex].translation.translatedText
                  : flashcards[currentFlashcardIndex].translation.originalText
                }
              </Typography>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ mt: 2, opacity: showAnswer ? 1 : 0 }}
              >
                {showAnswer && flashcards[currentFlashcardIndex].translation.pronunciation}
              </Typography>
            </Box>
          </CardContent>
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
            <IconButton onClick={() => handleFlashcardNavigation('prev')}>
              <ArrowBackIcon />
            </IconButton>
            <Typography>
              {currentFlashcardIndex + 1} / {flashcards.length}
            </Typography>
            <IconButton onClick={() => handleFlashcardNavigation('next')}>
              <ArrowForwardIcon />
            </IconButton>
          </Box>
        </Card>
      )}

      {/* Quiz */}
      {activeTab === 2 && (
        <Box>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : quizCompleted ? (
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  Quiz Completed!
                </Typography>
                <Typography variant="h6" color="primary">
                  Score: {quizScore} / {quizQuestions.length}
                </Typography>
                <Button
                  variant="contained"
                  onClick={startNewQuiz}
                  sx={{ mt: 2 }}
                >
                  Start New Quiz
                </Button>
              </CardContent>
            </Card>
          ) : quizQuestions.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Question {currentQuestionIndex + 1} of {quizQuestions.length}
                </Typography>
                <Typography variant="body1" sx={{ mb: 3 }}>
                  {quizQuestions[currentQuestionIndex].text}
                </Typography>
                <Grid container spacing={2}>
                  {quizQuestions[currentQuestionIndex].options.map((option, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <Button
                        variant="outlined"
                        fullWidth
                        onClick={() => handleAnswerSelection(option)}
                        disabled={selectedAnswer !== null}
                        color={
                          selectedAnswer === option
                            ? option === quizQuestions[currentQuestionIndex].correct_answer
                              ? 'success'
                              : 'error'
                            : 'primary'
                        }
                        sx={{ 
                          justifyContent: 'flex-start', 
                          textAlign: 'left',
                          p: 2,
                        }}
                      >
                        {option}
                      </Button>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}
        </Box>
      )}

      {/* Daily Learning */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Common Phrases
                </Typography>
                <List>
                  {/* Add common phrases list */}
                </List>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Learning Progress
                </Typography>
                {/* Add progress tracking visualization */}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Snackbar
        open={notification.open}
        autoHideDuration={3000}
        onClose={handleCloseNotification}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LearningTools; 