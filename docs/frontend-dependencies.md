# Frontend Dependencies Installation Guide

This guide explains how to install the required frontend dependencies for the learning tools revamp.

## Added Dependencies

We've added the following dependencies to the frontend:

1. **Google Authentication**:
   - `@react-oauth/google`: For Google OAuth integration
   - `jwt-decode`: For decoding JWT tokens

2. **UI Components**:
   - `@mui/lab`: Additional Material-UI components
   - `react-confetti`: For celebration animations on quiz completion
   - `react-markdown`: For rendering markdown content in quizzes
   - `react-syntax-highlighter`: For code highlighting in quizzes

## Installation Steps

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the dependencies:
   ```bash
   npm install
   ```

   Or if you prefer yarn:
   ```bash
   yarn
   ```

3. Verify installation:
   ```bash
   npm list @react-oauth/google @mui/lab react-confetti
   ```

## Usage Examples

### Google Authentication

```jsx
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';

const LoginButton = () => {
  const handleSuccess = (credentialResponse) => {
    const decoded = jwtDecode(credentialResponse.credential);
    console.log(decoded);
    // Send to backend for verification
  };

  return (
    <GoogleLogin
      onSuccess={handleSuccess}
      onError={() => console.log('Login Failed')}
    />
  );
};
```

### Quiz Components

```jsx
import { Timeline, TimelineItem, TimelineSeparator, TimelineConnector, TimelineContent, TimelineDot } from '@mui/lab';
import ReactConfetti from 'react-confetti';
import ReactMarkdown from 'react-markdown';

const QuizCompletion = ({ score, totalQuestions }) => {
  const passedQuiz = score > (totalQuestions / 2);
  
  return (
    <div>
      {passedQuiz && <ReactConfetti />}
      <h2>Quiz Results</h2>
      <p>You scored {score} out of {totalQuestions}</p>
      
      <ReactMarkdown>
        {`## Your Performance
- **Score**: ${score}/${totalQuestions}
- **Percentage**: ${Math.round((score/totalQuestions) * 100)}%
- **Status**: ${passedQuiz ? 'Passed' : 'Try Again'}`}
      </ReactMarkdown>
      
      <Timeline>
        {quizQuestions.map((q, index) => (
          <TimelineItem key={index}>
            <TimelineSeparator>
              <TimelineDot color={userAnswers[index].correct ? "success" : "error"} />
              {index < quizQuestions.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            <TimelineContent>
              <h4>Question {index + 1}</h4>
              <p>{q.question}</p>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </div>
  );
};
```

## Troubleshooting

If you encounter any issues during installation:

1. Clear npm cache:
   ```bash
   npm cache clean --force
   ```

2. Delete node_modules and reinstall:
   ```bash
   rm -rf node_modules
   npm install
   ```

3. Check for version conflicts:
   ```bash
   npm ls
   ```

4. Update npm:
   ```bash
   npm install -g npm@latest
   ```