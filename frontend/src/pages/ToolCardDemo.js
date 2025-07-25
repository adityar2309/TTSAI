import React from 'react';
import {
  Box,
  Typography,
  Container,
  Divider,
  Paper,
} from '@mui/material';
import {
  Quiz as QuizIcon,
  FlashOn as FlashOnIcon,
  School as SchoolIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';

// Import components
import ToolCard from '../components/learning/ToolCard';
import QuizCard from '../components/learning/QuizCard';
import FlashcardToolCard from '../components/learning/FlashcardToolCard';
import ChatbotCard from '../components/learning/ChatbotCard';
import ResponsiveGrid from '../components/learning/ResponsiveGrid';

/**
 * Demo page to showcase all tool card components
 */
const ToolCardDemo = () => {
  // Sample data for cards
  const sampleQuizzes = [
    {
      title: 'Beginner Grammar',
      description: 'Learn basic grammar rules and sentence structure',
      difficulty: 'beginner',
      questionCount: 10,
      timeLimit: 15,
      bestScore: 85,
    },
    {
      title: 'Intermediate Vocabulary',
      description: 'Expand your vocabulary with common phrases',
      difficulty: 'intermediate',
      questionCount: 15,
      timeLimit: 20,
      bestScore: 72,
      inProgress: true,
      progress: 60,
    },
    {
      title: 'Advanced Conversation',
      description: 'Test your knowledge of complex conversational patterns',
      difficulty: 'advanced',
      questionCount: 20,
      timeLimit: 30,
    },
  ];
  
  const sampleFlashcards = {
    totalCards: 48,
    dueCards: 12,
    masteredCards: 24,
    previewCards: [
      { front: 'Hello', back: 'Hola' },
      { front: 'Goodbye', back: 'Adiós' },
      { front: 'Thank you', back: 'Gracias' },
    ],
  };
  
  const sampleAvatars = [
    {
      name: 'Maria',
      image: '👩‍🏫',
      role: 'Spanish Teacher',
      recentMessages: [
        { sender: 'avatar', text: '¡Hola! ¿Cómo estás hoy?' },
        { sender: 'user', text: 'Estoy bien, gracias.' },
      ],
      totalConversations: 8,
      lastTopic: 'Travel Planning',
    },
    {
      name: 'Pierre',
      image: '👨‍🍳',
      role: 'French Chef',
      recentMessages: [
        { sender: 'avatar', text: 'Bonjour! Comment puis-je vous aider?' },
        { sender: 'user', text: 'Je voudrais apprendre le français.' },
      ],
      totalConversations: 3,
      lastTopic: 'Food & Dining',
    },
  ];
  
  // Event handlers (just console logs for demo)
  const handleAction = (action, data) => {
    console.log(`${action} action:`, data);
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Learning Tools Card Components
      </Typography>
      <Typography variant="body1" paragraph>
        This page demonstrates the various card components for the learning tools page.
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Basic Tool Cards
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <ResponsiveGrid>
          <ToolCard
            title="Flashcards"
            description="Review vocabulary with spaced repetition"
            icon={<FlashOnIcon />}
            iconColor="primary.main"
            content={
              <Box>
                <Typography variant="body2">
                  48 cards in your collection
                </Typography>
                <Typography variant="body2" color="primary">
                  12 cards due for review
                </Typography>
              </Box>
            }
            actionText="Review Cards"
            onAction={() => handleAction('flashcards')}
          />
          
          <ToolCard
            title="Quizzes"
            description="Test your knowledge with interactive quizzes"
            icon={<QuizIcon />}
            iconColor="secondary.main"
            content={
              <Box>
                <Typography variant="body2">
                  5 quizzes available
                </Typography>
                <Typography variant="body2" color="secondary">
                  Last score: 85%
                </Typography>
              </Box>
            }
            actionText="Start Quiz"
            onAction={() => handleAction('quizzes')}
            status="New"
            statusColor="success"
          />
          
          <ToolCard
            title="Lessons"
            description="Structured lessons to build your skills"
            icon={<SchoolIcon />}
            iconColor="info.main"
            content={
              <Box>
                <Typography variant="body2">
                  3 lesson paths available
                </Typography>
                <Typography variant="body2" color="info.main">
                  25% complete
                </Typography>
              </Box>
            }
            actionText="Continue Learning"
            onAction={() => handleAction('lessons')}
          />
          
          <ToolCard
            title="Conversation"
            description="Practice with AI language partners"
            icon={<ChatIcon />}
            iconColor="success.main"
            content={
              <Box>
                <Typography variant="body2">
                  2 conversation partners
                </Typography>
                <Typography variant="body2" color="success.main">
                  Last topic: Travel Planning
                </Typography>
              </Box>
            }
            actionText="Start Conversation"
            onAction={() => handleAction('conversation')}
            featured
          />
        </ResponsiveGrid>
      </Paper>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Quiz Cards
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <ResponsiveGrid>
          {sampleQuizzes.map((quiz, index) => (
            <QuizCard
              key={index}
              title={quiz.title}
              description={quiz.description}
              difficulty={quiz.difficulty}
              questionCount={quiz.questionCount}
              timeLimit={quiz.timeLimit}
              bestScore={quiz.bestScore}
              inProgress={quiz.inProgress}
              progress={quiz.progress}
              onStart={() => handleAction('start quiz', quiz)}
              onContinue={() => handleAction('continue quiz', quiz)}
            />
          ))}
        </ResponsiveGrid>
      </Paper>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Flashcard Tool Card
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <ResponsiveGrid md={6} lg={6}>
          <FlashcardToolCard
            totalCards={sampleFlashcards.totalCards}
            dueCards={sampleFlashcards.dueCards}
            masteredCards={sampleFlashcards.masteredCards}
            previewCards={sampleFlashcards.previewCards}
            onStartReview={() => handleAction('start flashcard review')}
            onCreateCard={() => handleAction('create flashcard')}
          />
          
          <FlashcardToolCard
            totalCards={0}
            dueCards={0}
            masteredCards={0}
            previewCards={[]}
            onStartReview={() => handleAction('start flashcard review')}
            onCreateCard={() => handleAction('create flashcard')}
          />
        </ResponsiveGrid>
      </Paper>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Chatbot Cards
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <ResponsiveGrid md={6} lg={6}>
          {sampleAvatars.map((avatar, index) => (
            <ChatbotCard
              key={index}
              avatar={avatar}
              recentMessages={avatar.recentMessages}
              totalConversations={avatar.totalConversations}
              lastTopic={avatar.lastTopic}
              onStartChat={() => handleAction('start chat', avatar)}
              onChangeAvatar={() => handleAction('change avatar')}
            />
          ))}
        </ResponsiveGrid>
      </Paper>
    </Container>
  );
};

export default ToolCardDemo;