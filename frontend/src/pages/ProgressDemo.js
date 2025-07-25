import React from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Divider,
} from '@mui/material';

// Import components
import ProgressSummary from '../components/learning/ProgressSummary';
import DetailedStats from '../components/learning/DetailedStats';
import AchievementsDisplay from '../components/learning/AchievementsDisplay';

/**
 * Demo page to showcase progress and statistics components
 */
const ProgressDemo = () => {
  // Sample user data
  const sampleUser = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    profilePicture: null,
  };
  
  // Sample progress data
  const sampleProgress = {
    level: 5,
    xp: 1250,
    xpToNext: 1500,
    streak: 12,
    wordsLearned: 156,
    quizzesCompleted: 23,
    conversationMinutes: 180,
  };
  
  // Sample detailed stats
  const sampleStats = {
    totalStudyTime: 720, // 12 hours
    averageSessionTime: 25,
    accuracyRate: 78,
    improvementRate: 15,
  };
  
  // Sample weekly progress
  const sampleWeeklyProgress = {
    currentWeek: 85,
    lastWeek: 72,
    target: 100,
  };
  
  // Sample skill levels
  const sampleSkillLevels = [
    { skill: 'Vocabulary', level: 75, target: 80 },
    { skill: 'Grammar', level: 60, target: 70 },
    { skill: 'Listening', level: 55, target: 75 },
    { skill: 'Speaking', level: 45, target: 65 },
    { skill: 'Reading', level: 80, target: 85 },
    { skill: 'Writing', level: 40, target: 60 },
  ];
  
  // Sample achievements
  const sampleAchievements = [
    {
      id: 'first-steps',
      name: 'First Steps',
      description: 'Complete your first lesson',
      icon: '👶',
      unlocked: true,
      unlockedAt: '2024-01-15',
      category: 'Getting Started',
      rarity: 'common',
      points: 10,
    },
    {
      id: 'week-warrior',
      name: 'Week Warrior',
      description: 'Maintain a 7-day learning streak',
      icon: '🔥',
      unlocked: true,
      unlockedAt: '2024-01-22',
      category: 'Consistency',
      rarity: 'uncommon',
      points: 25,
    },
    {
      id: 'quiz-master',
      name: 'Quiz Master',
      description: 'Complete 10 quizzes with 80% or higher',
      icon: '🏆',
      unlocked: false,
      progress: 7,
      target: 10,
      category: 'Mastery',
      rarity: 'rare',
      points: 50,
    },
    {
      id: 'vocabulary-expert',
      name: 'Vocabulary Expert',
      description: 'Learn 100 new words',
      icon: '📚',
      unlocked: false,
      progress: 65,
      target: 100,
      category: 'Learning',
      rarity: 'uncommon',
      points: 30,
    },
    {
      id: 'conversation-king',
      name: 'Conversation King',
      description: 'Have 50 conversations with AI avatars',
      icon: '👑',
      unlocked: false,
      progress: 12,
      target: 50,
      category: 'Practice',
      rarity: 'epic',
      points: 100,
    },
    {
      id: 'perfectionist',
      name: 'Perfectionist',
      description: 'Get 100% on 5 consecutive quizzes',
      icon: '💎',
      unlocked: false,
      progress: 2,
      target: 5,
      category: 'Excellence',
      rarity: 'legendary',
      points: 200,
    },
  ];
  
  // Handle achievement click
  const handleAchievementClick = (achievement) => {
    console.log('Achievement clicked:', achievement);
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Progress and Statistics Components
      </Typography>
      <Typography variant="body1" paragraph>
        This page demonstrates the progress tracking and statistics components for the learning tools page.
      </Typography>
      
      {/* Progress Summary */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Progress Summary
        </Typography>
        <Typography variant="body2" paragraph>
          Main progress overview with user info, level progress, and key statistics.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <ProgressSummary
          user={sampleUser}
          progress={sampleProgress}
          achievements={sampleAchievements}
          showAchievements={true}
          showStats={true}
        />
      </Paper>
      
      {/* Detailed Statistics */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Detailed Statistics
        </Typography>
        <Typography variant="body2" paragraph>
          Comprehensive statistics including study time, accuracy, weekly progress, and skill levels.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <DetailedStats
          stats={sampleStats}
          weeklyProgress={sampleWeeklyProgress}
          skillLevels={sampleSkillLevels}
        />
      </Paper>
      
      {/* Achievements Display */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Achievements Display
        </Typography>
        <Typography variant="body2" paragraph>
          Achievement system with unlocked and locked achievements, progress tracking, and rarity levels.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <AchievementsDisplay
          achievements={sampleAchievements}
          onAchievementClick={handleAchievementClick}
          showProgress={true}
        />
      </Paper>
      
      {/* Minimal Progress Summary */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Minimal Progress Summary
        </Typography>
        <Typography variant="body2" paragraph>
          Simplified version with only essential progress information.
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <ProgressSummary
          user={sampleUser}
          progress={sampleProgress}
          showAchievements={false}
          showStats={false}
        />
      </Paper>
    </Container>
  );
};

export default ProgressDemo;