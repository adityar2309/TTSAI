# Frontend Dependencies Usage Guide

This guide provides quick examples of how to use the newly installed dependencies for the Learning Tools Revamp project.

## Form Handling with React Hook Form

### Basic Form Setup
```jsx
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

const schema = yup.object({
  answer: yup.string().required('Answer is required'),
  email: yup.string().email('Invalid email').required('Email is required')
});

function QuizForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  const onSubmit = (data) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('answer')} placeholder="Your answer" />
      {errors.answer && <p>{errors.answer.message}</p>}
      
      <button type="submit">Submit</button>
    </form>
  );
}
```

## Data Management with React Query

### Basic Query Setup
```jsx
import { useQuery, QueryClient, QueryClientProvider } from '@tanstack/react-query';
import axios from 'axios';

// In your App.js
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourComponent />
    </QueryClientProvider>
  );
}

// In your component
function QuizList() {
  const { data: quizzes, isLoading, error } = useQuery({
    queryKey: ['quizzes'],
    queryFn: () => axios.get('/api/quizzes').then(res => res.data)
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {quizzes.map(quiz => (
        <div key={quiz.id}>{quiz.title}</div>
      ))}
    </div>
  );
}
```

## Animations with Framer Motion

### Basic Animations
```jsx
import { motion } from 'framer-motion';

function AnimatedCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <h3>Quiz Card</h3>
      <p>Click me!</p>
    </motion.div>
  );
}
```

### Page Transitions
```jsx
import { motion, AnimatePresence } from 'framer-motion';

function PageTransition({ children, key }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={key}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

## Spring Animations with React Spring

### Basic Spring Animation
```jsx
import { useSpring, animated } from 'react-spring';

function SpringCard() {
  const [flip, setFlip] = useState(false);
  const { transform, opacity } = useSpring({
    opacity: flip ? 1 : 0,
    transform: `perspective(600px) rotateX(${flip ? 180 : 0}deg)`,
    config: { mass: 5, tension: 500, friction: 80 }
  });

  return (
    <animated.div
      style={{ opacity, transform }}
      onClick={() => setFlip(!flip)}
    >
      Card content
    </animated.div>
  );
}
```

## Quiz Timer with Countdown Circle Timer

```jsx
import { CountdownCircleTimer } from 'react-countdown-circle-timer';

function QuizTimer({ duration, onComplete }) {
  return (
    <CountdownCircleTimer
      isPlaying
      duration={duration}
      colors={['#004777', '#F7B801', '#A30000', '#A30000']}
      colorsTime={[10, 6, 3, 0]}
      onComplete={onComplete}
    >
      {({ remainingTime }) => remainingTime}
    </CountdownCircleTimer>
  );
}
```

## Data Visualization with MUI X Charts

### Line Chart for Progress
```jsx
import { LineChart } from '@mui/x-charts/LineChart';

function ProgressChart({ data }) {
  return (
    <LineChart
      width={500}
      height={300}
      series={[
        {
          data: data.scores,
          label: 'Quiz Scores',
        },
      ]}
      xAxis={[{ scaleType: 'point', data: data.dates }]}
    />
  );
}
```

### Data Grid for Results
```jsx
import { DataGrid } from '@mui/x-data-grid';

function QuizResults({ results }) {
  const columns = [
    { field: 'id', headerName: 'ID', width: 90 },
    { field: 'quiz', headerName: 'Quiz', width: 150 },
    { field: 'score', headerName: 'Score', width: 110 },
    { field: 'date', headerName: 'Date', width: 160 },
  ];

  return (
    <div style={{ height: 400, width: '100%' }}>
      <DataGrid
        rows={results}
        columns={columns}
        pageSize={5}
        rowsPerPageOptions={[5]}
        checkboxSelection
      />
    </div>
  );
}
```

## Date Picker for Scheduling

```jsx
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

function SchedulePicker() {
  const [value, setValue] = useState(new Date());

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <DatePicker
        label="Select Date"
        value={value}
        onChange={(newValue) => setValue(newValue)}
      />
    </LocalizationProvider>
  );
}
```

## Keyboard Shortcuts with React Hotkeys Hook

```jsx
import { useHotkeys } from 'react-hotkeys-hook';

function QuizComponent() {
  const [currentQuestion, setCurrentQuestion] = useState(0);

  useHotkeys('ctrl+n', () => setCurrentQuestion(prev => prev + 1));
  useHotkeys('ctrl+p', () => setCurrentQuestion(prev => prev - 1));
  useHotkeys('enter', () => submitAnswer());
  useHotkeys('escape', () => exitQuiz());

  return (
    <div>
      <p>Use Ctrl+N for next, Ctrl+P for previous, Enter to submit, Esc to exit</p>
      {/* Quiz content */}
    </div>
  );
}
```

## Recharts for Custom Charts

```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function CustomProgressChart({ data }) {
  return (
    <LineChart width={500} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="score" stroke="#8884d8" />
      <Line type="monotone" dataKey="time" stroke="#82ca9d" />
    </LineChart>
  );
}
```

## Testing with React Testing Library

```jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import QuizComponent from './QuizComponent';

test('submits quiz answer', async () => {
  const user = userEvent.setup();
  render(<QuizComponent />);
  
  const answerInput = screen.getByLabelText(/answer/i);
  const submitButton = screen.getByRole('button', { name: /submit/i });
  
  await user.type(answerInput, 'My answer');
  await user.click(submitButton);
  
  expect(screen.getByText(/submitted/i)).toBeInTheDocument();
});
```

## Best Practices

1. **React Query**: Use query keys consistently and implement proper error handling
2. **Framer Motion**: Keep animations subtle and performance-focused
3. **React Hook Form**: Use schema validation for complex forms
4. **Material-UI X**: Consider licensing requirements for production use
5. **Testing**: Write tests for user interactions, not implementation details

## Performance Tips

- Use React.memo() for components with expensive animations
- Implement proper loading states with React Query
- Use React Spring for physics-based animations that feel natural
- Optimize chart rendering by limiting data points
- Use proper key props for animated lists