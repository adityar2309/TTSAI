import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  LinearProgress,
  Box
} from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import sessionService from '../../services/sessionService';

const SessionTimeoutWarning = () => {
  const [open, setOpen] = useState(false);
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes in seconds
  const [progress, setProgress] = useState(100);
  const { refreshToken, logout } = useAuth();
  
  // Set up session warning handler
  useEffect(() => {
    const handleSessionWarning = (minutesLeft) => {
      setTimeLeft(minutesLeft * 60);
      setOpen(true);
    };
    
    // Initialize session service with warning handler
    sessionService.init(
      () => logout(), // Session expired handler
      handleSessionWarning // Session warning handler
    );
    
    return () => {
      // Clean up timers
      sessionService.clearTimers();
    };
  }, [logout]);
  
  // Countdown timer
  useEffect(() => {
    let timer;
    
    if (open && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft(prev => {
          const newTime = prev - 1;
          setProgress((newTime / 300) * 100);
          return newTime;
        });
      }, 1000);
    } else if (timeLeft <= 0 && open) {
      // Session expired
      setOpen(false);
      logout();
    }
    
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [open, timeLeft, logout]);
  
  // Format time as MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };
  
  // Handle continue session
  const handleContinue = async () => {
    const success = await refreshToken();
    if (success) {
      setOpen(false);
    }
  };
  
  // Handle logout
  const handleLogout = () => {
    setOpen(false);
    logout();
  };
  
  return (
    <Dialog
      open={open}
      onClose={(e, reason) => {
        // Prevent closing by clicking outside
        if (reason !== 'backdropClick') {
          setOpen(false);
        }
      }}
    >
      <DialogTitle>Session Timeout Warning</DialogTitle>
      <DialogContent>
        <Typography variant="body1" gutterBottom>
          Your session will expire in {formatTime(timeLeft)}. Would you like to continue?
        </Typography>
        <Box sx={{ width: '100%', mt: 2, mb: 1 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            color={progress < 30 ? "error" : progress < 70 ? "warning" : "primary"} 
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleLogout} color="error">
          Logout
        </Button>
        <Button onClick={handleContinue} variant="contained" color="primary" autoFocus>
          Continue Session
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SessionTimeoutWarning;