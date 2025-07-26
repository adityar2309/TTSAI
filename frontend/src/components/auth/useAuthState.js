import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { jwtDecode } from 'jwt-decode';

/**
 * Enhanced authentication hook with additional state management
 */
export const useAuthState = () => {
  const auth = useAuth();
  const [sessionInfo, setSessionInfo] = useState({
    timeUntilExpiry: null,
    isExpiringSoon: false,
    lastActivity: Date.now()
  });

  // Update last activity timestamp
  const updateActivity = useCallback(() => {
    setSessionInfo(prev => ({
      ...prev,
      lastActivity: Date.now()
    }));
  }, []);

  // Calculate session info from token
  useEffect(() => {
    if (!auth.token) {
      setSessionInfo({
        timeUntilExpiry: null,
        isExpiringSoon: false,
        lastActivity: Date.now()
      });
      return;
    }

    const updateSessionInfo = () => {
      try {
        const decoded = jwtDecode(auth.token);
        const currentTime = Date.now() / 1000;
        const timeUntilExpiry = decoded.exp - currentTime;
        const isExpiringSoon = timeUntilExpiry < 300; // 5 minutes

        setSessionInfo(prev => ({
          ...prev,
          timeUntilExpiry: Math.max(0, timeUntilExpiry),
          isExpiringSoon
        }));
      } catch (error) {
        console.error('Error calculating session info:', error);
      }
    };

    // Update immediately
    updateSessionInfo();

    // Update every minute
    const interval = setInterval(updateSessionInfo, 60000);

    return () => clearInterval(interval);
  }, [auth.token]);

  // Set up activity listeners
  useEffect(() => {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    
    events.forEach(event => {
      document.addEventListener(event, updateActivity, true);
    });

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity, true);
      });
    };
  }, [updateActivity]);

  return {
    ...auth,
    sessionInfo,
    updateActivity,
    
    // Computed properties
    isSessionExpiringSoon: sessionInfo.isExpiringSoon,
    timeUntilExpiry: sessionInfo.timeUntilExpiry,
    lastActivity: sessionInfo.lastActivity,
    
    // Helper methods
    getTimeUntilExpiryFormatted: () => {
      if (!sessionInfo.timeUntilExpiry) return null;
      
      const minutes = Math.floor(sessionInfo.timeUntilExpiry / 60);
      const seconds = Math.floor(sessionInfo.timeUntilExpiry % 60);
      
      return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    },
    
    isTokenExpired: () => {
      return sessionInfo.timeUntilExpiry !== null && sessionInfo.timeUntilExpiry <= 0;
    },
    
    getInactivityTime: () => {
      return Date.now() - sessionInfo.lastActivity;
    },
    
    isInactive: (thresholdMs = 30 * 60 * 1000) => { // 30 minutes default
      return Date.now() - sessionInfo.lastActivity > thresholdMs;
    }
  };
};

export default useAuthState;