import React, { useState, useEffect, useRef } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio,
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
  Send as SendIcon,
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
    if (language && language.trim() !== '') {
      fetchWordOfDay();
      fetchFlashcards();
      fetchProgress();
    }
  }, [language]);

  const fetchWordOfDay = async () => {
    try {
      if (!language || language.trim() === '') {
        console.warn('Language not set, skipping word of day fetch');
        return;
      }

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
      if (!language || language.trim() === '') {
        console.warn('Language not set, skipping flashcards fetch');
        return;
      }

      const response = await axios.get(`${API_URL}/flashcards`, {
        params: { userId, language }
      });
      
      // Handle new response format from SQLite backend
      const flashcardsData = response.data.flashcards || response.data || [];
      setFlashcards(flashcardsData);
    } catch (err) {
      console.error('Error fetching flashcards:', err);
      setError('Failed to fetch flashcards');
    }
  };

  const fetchProgress = async () => {
    try {
      if (!language || language.trim() === '') {
        console.warn('Language not set, skipping progress fetch');
        return;
      }

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

  const ConversationMode = ({ language, userId }) => {
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const [context, setContext] = useState('general');
    const [proficiency, setProficiency] = useState('beginner');
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);
    const messagesEndRef = useRef(null);

    const contexts = [
      { value: 'general', label: 'General Conversation' },
      { value: 'travel', label: 'Travel & Directions' },
      { value: 'restaurant', label: 'Restaurant & Food' },
      { value: 'business', label: 'Business & Work' },
      { value: 'shopping', label: 'Shopping' },
      { value: 'emergency', label: 'Emergency Situations' },
    ];

    const proficiencyLevels = [
      { value: 'beginner', label: 'Beginner' },
      { value: 'intermediate', label: 'Intermediate' },
      { value: 'advanced', label: 'Advanced' },
    ];

    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
      scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (!userInput.trim()) return;

      const newMessage = {
        type: 'user',
        text: userInput,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, newMessage]);
      setUserInput('');
      setLoading(true);

      try {
        const response = await axios.post(`${API_URL}/conversation`, {
          text: userInput,
          language,
          userId,
          context,
          proficiency,
        });

        const aiResponse = {
          type: 'ai',
          response: response.data.ai_response,
          translation: response.data.translation,
          vocabulary: response.data.vocabulary,
          grammar_notes: response.data.grammar_notes,
          cultural_note: response.data.cultural_note,
          suggested_responses: response.data.suggested_responses,
          timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, aiResponse]);
        setStats(response.data.stats);
      } catch (err) {
        console.error('Error in conversation:', err);
        setNotification({
          open: true,
          message: 'Failed to get response',
          severity: 'error',
        });
      } finally {
        setLoading(false);
      }
    };

    return (
      <Card elevation={3}>
        <CardContent>
          <Stack direction="row" alignItems="center" spacing={1} mb={2}>
            <SchoolIcon color="primary" />
            <Typography variant="h6">Interactive Conversation</Typography>
          </Stack>

          <Grid container spacing={2} mb={2}>
            <Grid item xs={12} sm={6}>
              <Box sx={{ minWidth: 120 }}>
                <FormControl fullWidth>
                  <InputLabel>Context</InputLabel>
                  <Select
                    value={context}
                    label="Context"
                    onChange={(e) => setContext(e.target.value)}
                  >
                    {contexts.map(ctx => (
                      <MenuItem key={ctx.value} value={ctx.value}>
                        {ctx.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box sx={{ minWidth: 120 }}>
                <FormControl fullWidth>
                  <InputLabel>Proficiency</InputLabel>
                  <Select
                    value={proficiency}
                    label="Proficiency"
                    onChange={(e) => setProficiency(e.target.value)}
                  >
                    {proficiencyLevels.map(level => (
                      <MenuItem key={level.value} value={level.value}>
                        {level.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
            </Grid>
          </Grid>

          <Paper 
            elevation={0} 
            sx={{ 
              height: 400, 
              p: 2, 
              mb: 2, 
              overflow: 'auto',
              bgcolor: 'background.default'
            }}
          >
            {messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  mb: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: msg.type === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    maxWidth: '80%',
                    bgcolor: msg.type === 'user' ? 'primary.light' : 'background.paper',
                    color: msg.type === 'user' ? 'primary.contrastText' : 'text.primary',
                  }}
                >
                  {msg.type === 'user' ? (
                    <Typography>{msg.text}</Typography>
                  ) : (
                    <Stack spacing={1}>
                      <Typography variant="body1" color="primary">
                        {msg.response}
                      </Typography>
                      <Typography variant="body2">
                        {msg.translation}
                      </Typography>
                      <Divider />
                      <Typography variant="caption" color="text.secondary">
                        Key Vocabulary:
                      </Typography>
                      <Box>
                        {msg.vocabulary?.map((word, i) => (
                          <Chip
                            key={i}
                            label={word}
                            size="small"
                            sx={{ m: 0.5 }}
                            onClick={() => playAudio(word)}
                          />
                        ))}
                      </Box>
                      {msg.grammar_notes && (
                        <>
                          <Typography variant="caption" color="text.secondary">
                            Grammar Points:
                          </Typography>
                          <Typography variant="body2">
                            {msg.grammar_notes}
                          </Typography>
                        </>
                      )}
                      {msg.cultural_note && (
                        <Alert severity="info" sx={{ mt: 1 }}>
                          {msg.cultural_note}
                        </Alert>
                      )}
                    </Stack>
                  )}
                </Paper>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </Typography>
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </Paper>

          <form onSubmit={handleSubmit}>
            <Stack direction="row" spacing={2}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Type your message..."
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                disabled={loading}
              />
              <IconButton 
                type="submit" 
                color="primary" 
                disabled={loading || !userInput.trim()}
                sx={{ p: '10px' }}
              >
                {loading ? <CircularProgress size={24} /> : <SendIcon />}
              </IconButton>
            </Stack>
          </form>

          {stats && (
            <Box mt={2}>
              <Typography variant="caption" color="text.secondary">
                Total Conversations: {stats.conversations} | Messages: {stats.total_messages}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  const QuizMode = ({ language, userId }) => {
    const [quiz, setQuiz] = useState(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [quizType, setQuizType] = useState('mixed');
    const [difficulty, setDifficulty] = useState('beginner');
    const [feedback, setFeedback] = useState(null);
    const [stats, setStats] = useState(null);

    const quizTypes = [
      { value: 'mixed', label: 'Mixed Quiz' },
      { value: 'vocabulary', label: 'Vocabulary' },
      { value: 'grammar', label: 'Grammar' },
      { value: 'conversation', label: 'Conversation' },
    ];

    const difficultyLevels = [
      { value: 'beginner', label: 'Beginner' },
      { value: 'intermediate', label: 'Intermediate' },
      { value: 'advanced', label: 'Advanced' },
    ];

    const startQuiz = async () => {
      setLoading(true);
      try {
        const response = await axios.post(`${API_URL}/quiz/generate`, {
          userId,
          language,
          type: quizType,
          difficulty,
        });

        setQuiz(response.data);
        setCurrentQuestionIndex(0);
        setSelectedAnswer('');
        setFeedback(null);
      } catch (err) {
        console.error('Error starting quiz:', err);
        setNotification({
          open: true,
          message: 'Failed to start quiz',
          severity: 'error',
        });
      } finally {
        setLoading(false);
      }
    };

    const handleAnswerSubmit = async () => {
      if (!selectedAnswer) return;

      setLoading(true);
      try {
        const response = await axios.post(`${API_URL}/quiz/${quiz.quiz_id}/submit`, {
          userId,
          answer: selectedAnswer,
          questionIndex: currentQuestionIndex,
        });

        setFeedback({
          correct: response.data.correct,
          explanation: response.data.explanation,
          points: response.data.points_earned,
        });

        if (response.data.completed) {
          setStats({
            score: response.data.total_score,
            completed: true,
          });
        }
      } catch (err) {
        console.error('Error submitting answer:', err);
        setNotification({
          open: true,
          message: 'Failed to submit answer',
          severity: 'error',
        });
      } finally {
        setLoading(false);
      }
    };

    const handleNextQuestion = () => {
      setCurrentQuestionIndex(prev => prev + 1);
      setSelectedAnswer('');
      setFeedback(null);
    };

    const renderQuestion = () => {
      if (!quiz || !quiz.questions[currentQuestionIndex]) return null;

      const question = quiz.questions[currentQuestionIndex];

      return (
        <Box>
          {question.type === 'conversation' && (
            <Alert severity="info" sx={{ mb: 2 }}>
              {question.scenario}
            </Alert>
          )}

          <Typography variant="h6" gutterBottom>
            {question.text}
          </Typography>

          {question.type === 'multiple_choice' || question.type === 'conversation' ? (
            <RadioGroup
              value={selectedAnswer}
              onChange={(e) => setSelectedAnswer(e.target.value)}
            >
              {question.options.map((option, index) => (
                <FormControlLabel
                  key={index}
                  value={option}
                  control={<Radio />}
                  label={option}
                  disabled={!!feedback}
                />
              ))}
            </RadioGroup>
          ) : question.type === 'translation' ? (
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your translation..."
              value={selectedAnswer}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              disabled={!!feedback}
              sx={{ mt: 2 }}
            />
          ) : question.type === 'fill_blank' ? (
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Fill in the blank..."
              value={selectedAnswer}
              onChange={(e) => setSelectedAnswer(e.target.value)}
              disabled={!!feedback}
              sx={{ mt: 2 }}
            />
          ) : null}

          {question.hint && !feedback && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Hint: {question.hint}
            </Alert>
          )}

          {feedback && (
            <Box mt={2}>
              <Alert severity={feedback.correct ? 'success' : 'error'}>
                {feedback.correct ? 'Correct!' : 'Incorrect'} (+{feedback.points} points)
              </Alert>
              {feedback.explanation && (
                <Paper sx={{ p: 2, mt: 1, bgcolor: 'background.default' }}>
                  <Typography variant="body2">
                    {feedback.explanation}
                  </Typography>
                </Paper>
              )}
            </Box>
          )}

          <Box mt={2} display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              Question {currentQuestionIndex + 1} of {quiz.total_questions}
            </Typography>
            <Box>
              {!feedback ? (
                <Button
                  variant="contained"
                  onClick={handleAnswerSubmit}
                  disabled={!selectedAnswer || loading}
                >
                  Submit Answer
                </Button>
              ) : currentQuestionIndex < quiz.total_questions - 1 ? (
                <Button
                  variant="contained"
                  onClick={handleNextQuestion}
                  disabled={loading}
                >
                  Next Question
                </Button>
              ) : null}
            </Box>
          </Box>
        </Box>
      );
    };

    return (
      <Card elevation={3}>
        <CardContent>
          <Stack direction="row" alignItems="center" spacing={1} mb={2}>
            <QuizIcon color="primary" />
            <Typography variant="h6">Practice Quiz</Typography>
          </Stack>

          {!quiz ? (
            <Box>
              <Grid container spacing={2} mb={2}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Quiz Type</InputLabel>
                    <Select
                      value={quizType}
                      label="Quiz Type"
                      onChange={(e) => setQuizType(e.target.value)}
                    >
                      {quizTypes.map(type => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Difficulty</InputLabel>
                    <Select
                      value={difficulty}
                      label="Difficulty"
                      onChange={(e) => setDifficulty(e.target.value)}
                    >
                      {difficultyLevels.map(level => (
                        <MenuItem key={level.value} value={level.value}>
                          {level.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Button
                variant="contained"
                fullWidth
                onClick={startQuiz}
                disabled={loading}
              >
                Start Quiz
              </Button>
            </Box>
          ) : stats?.completed ? (
            <Box textAlign="center">
              <Typography variant="h4" color="primary" gutterBottom>
                Quiz Completed!
              </Typography>
              <Typography variant="h5" gutterBottom>
                Final Score: {stats.score} points
              </Typography>
              <Button
                variant="contained"
                onClick={() => {
                  setQuiz(null);
                  setStats(null);
                }}
                sx={{ mt: 2 }}
              >
                Start New Quiz
              </Button>
            </Box>
          ) : (
            renderQuestion()
          )}
        </CardContent>
      </Card>
    );
  };

  const ProgressMode = ({ language, userId }) => {
    const [progress, setProgress] = useState(null);
    const [loading, setLoading] = useState(false);
    const [timeRange, setTimeRange] = useState('week');  // week, month, all

    useEffect(() => {
      fetchProgress();
    }, [language, userId, timeRange]);

    const fetchProgress = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`${API_URL}/progress`, {
          params: { userId, language, timeRange }
        });
        setProgress(response.data);
      } catch (err) {
        console.error('Error fetching progress:', err);
        setNotification({
          open: true,
          message: 'Failed to fetch progress',
          severity: 'error',
        });
      } finally {
        setLoading(false);
      }
    };

    const calculateLevel = (xp) => {
      const baseXP = 1000;
      const level = Math.floor(Math.log2(xp / baseXP + 1)) + 1;
      const nextLevelXP = baseXP * (Math.pow(2, level) - 1);
      const progress = ((xp - (baseXP * (Math.pow(2, level - 1) - 1))) / (nextLevelXP - (baseXP * (Math.pow(2, level - 1) - 1)))) * 100;
      return { level, progress };
    };

    if (loading) {
      return (
        <Card elevation={3}>
          <CardContent>
            <Box display="flex" justifyContent="center" p={4}>
              <CircularProgress />
            </Box>
          </CardContent>
        </Card>
      );
    }

    return (
      <Card elevation={3}>
        <CardContent>
          <Stack direction="row" alignItems="center" spacing={1} mb={2}>
            <TimelineIcon color="primary" />
            <Typography variant="h6">Learning Progress</Typography>
          </Stack>

          <Grid container spacing={3}>
            {/* Time Range Selector */}
            <Grid item xs={12}>
              <Box sx={{ minWidth: 120 }}>
                <FormControl fullWidth>
                  <InputLabel>Time Range</InputLabel>
                  <Select
                    value={timeRange}
                    label="Time Range"
                    onChange={(e) => setTimeRange(e.target.value)}
                  >
                    <MenuItem value="week">Past Week</MenuItem>
                    <MenuItem value="month">Past Month</MenuItem>
                    <MenuItem value="all">All Time</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Grid>

            {progress && (
              <>
                {/* Level Progress */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                    <Stack spacing={2} alignItems="center">
                      <Typography variant="h6" color="primary">
                        Level {calculateLevel(progress.total_xp).level}
                      </Typography>
                      <Box position="relative" display="inline-flex">
                        <CircularProgress
                          variant="determinate"
                          value={calculateLevel(progress.total_xp).progress}
                          size={120}
                        />
                        <Box
                          sx={{
                            top: 0,
                            left: 0,
                            bottom: 0,
                            right: 0,
                            position: 'absolute',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <Typography variant="caption" color="text.secondary">
                            {Math.round(calculateLevel(progress.total_xp).progress)}%
                          </Typography>
                        </Box>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        Total XP: {progress.total_xp}
                      </Typography>
                    </Stack>
                  </Paper>
                </Grid>

                {/* Quiz Performance */}
                <Grid item xs={12} md={6}>
                  <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                    <Stack spacing={2}>
                      <Typography variant="h6" gutterBottom>
                        Quiz Performance
                      </Typography>
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Average Score
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={progress.average_score}
                          sx={{ height: 10, borderRadius: 5 }}
                        />
                        <Typography variant="body2" color="text.secondary" mt={1}>
                          {Math.round(progress.average_score)}%
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Quizzes Completed: {progress.quizzes_completed}
                        </Typography>
                      </Box>
                    </Stack>
                  </Paper>
                </Grid>

                {/* Activity Stats */}
                <Grid item xs={12}>
                  <Paper elevation={2} sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Activity Stats
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6} sm={3}>
                        <Stack alignItems="center">
                          <Typography variant="h4" color="primary">
                            {progress.streak_days}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Day Streak
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Stack alignItems="center">
                          <Typography variant="h4" color="primary">
                            {progress.words_learned}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Words Learned
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Stack alignItems="center">
                          <Typography variant="h4" color="primary">
                            {progress.conversations}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Conversations
                          </Typography>
                        </Stack>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Stack alignItems="center">
                          <Typography variant="h4" color="primary">
                            {Math.round(progress.study_time / 60)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Hours Studied
                          </Typography>
                        </Stack>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>

                {/* Achievements */}
                {progress.achievements && progress.achievements.length > 0 && (
                  <Grid item xs={12}>
                    <Paper elevation={2} sx={{ p: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        Recent Achievements
                      </Typography>
                      <Grid container spacing={2}>
                        {progress.achievements.map((achievement, index) => (
                          <Grid item xs={12} sm={6} md={4} key={index}>
                            <Paper
                              elevation={1}
                              sx={{
                                p: 2,
                                display: 'flex',
                                alignItems: 'center',
                                gap: 2,
                                bgcolor: achievement.unlocked ? 'primary.light' : 'background.default',
                              }}
                            >
                              <EmojiEventsIcon
                                color={achievement.unlocked ? 'primary' : 'disabled'}
                              />
                              <Box>
                                <Typography variant="subtitle2">
                                  {achievement.title}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {achievement.description}
                                </Typography>
                              </Box>
                            </Paper>
                          </Grid>
                        ))}
                      </Grid>
                    </Paper>
                  </Grid>
                )}
              </>
            )}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto' }}>
      {/* Show message if language is not set */}
      {(!language || language.trim() === '') ? (
        <Card elevation={3}>
          <CardContent>
            <Box display="flex" flexDirection="column" alignItems="center" p={4}>
              <SchoolIcon color="primary" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Select a Language to Start Learning
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                Please select a target language in the translator to access learning tools.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <>
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
                        "{wordOfDay.example_sentence}"
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

              {/* Conversation Mode */}
              <ConversationMode language={language} userId={userId} />

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
            <QuizMode language={language} userId={userId} />
          )}

          {/* Progress Tab */}
          {activeTab === 2 && (
            <ProgressMode language={language} userId={userId} />
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
        </>
      )}
    </Box>
  );
};

export default LearningTools; 