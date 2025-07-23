import { jwtDecode } from 'jwt-decode';
import api, { authEvents } from '../utils/apiClient';

// Token storage key
const TOKEN_KEY = 'authToken';

// Session refresh interval (15 minutes)
const REFRESH_INTERVAL = 15 * 60 * 1000;

// Session timeout warning (5 minutes before expiry)
const WARNING_BEFORE_TIMEOUT = 5 * 60 * 1000;

let refreshTimer = null;
let warningTimer = null;

/**
 * Session management service
 */
const sessionService = {
  /**
   * Initialize session management
   * @param {Function} onSessionExpired - Callback when session expires
   * @param {Function} onSessionWarning - Callback when session is about to expire
   */
  init: (onSessionExpired, onSessionWarning) => {
    // Clear any existing timers
    sessionService.clearTimers();
    
    // Add listener for auth errors
    authEvents.addListener('authError', () => {
      if (onSessionExpired) {
        onSessionExpired();
      }
    });
    
    // Check for existing token and set up refresh
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      sessionService.setupTokenRefresh(token, onSessionWarning);
    }
  },
  
  /**
   * Set up token refresh and warning timers
   * @param {string} token - JWT token
   * @param {Function} onSessionWarning - Callback when session is about to expire
   */
  setupTokenRefresh: (token, onSessionWarning) => {
    try {
      // Decode token to get expiration
      const decoded = jwtDecode(token);
      
      if (!decoded.exp) {
        console.error('Token does not contain expiration');
        return;
      }
      
      // Calculate expiration time in milliseconds
      const expiryTime = decoded.exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();
      const timeUntilExpiry = expiryTime - currentTime;
      
      // If token is already expired
      if (timeUntilExpiry <= 0) {
        console.log('Token already expired');
        sessionService.clearSession();
        return;
      }
      
      // Set up refresh timer (refresh at interval or before expiry, whichever is sooner)
      const refreshTime = Math.min(REFRESH_INTERVAL, timeUntilExpiry - 60000); // 1 minute before expiry
      
      console.log(`Setting up token refresh in ${refreshTime / 1000} seconds`);
      
      refreshTimer = setTimeout(() => {
        sessionService.refreshToken();
      }, refreshTime);
      
      // Set up warning timer if expiry is far enough in the future
      if (timeUntilExpiry > WARNING_BEFORE_TIMEOUT) {
        const warningTime = timeUntilExpiry - WARNING_BEFORE_TIMEOUT;
        
        console.log(`Setting up session warning in ${warningTime / 1000} seconds`);
        
        warningTimer = setTimeout(() => {
          if (onSessionWarning) {
            onSessionWarning(WARNING_BEFORE_TIMEOUT / 1000 / 60); // Minutes until expiry
          }
        }, warningTime);
      }
    } catch (error) {
      console.error('Error setting up token refresh:', error);
      sessionService.clearSession();
    }
  },
  
  /**
   * Refresh the authentication token
   * @returns {Promise<boolean>} Success status
   */
  refreshToken: async () => {
    try {
      // Clear existing timers
      sessionService.clearTimers();
      
      // Get current token
      const currentToken = localStorage.getItem(TOKEN_KEY);
      
      if (!currentToken) {
        return false;
      }
      
      // Call refresh endpoint
      const response = await api.auth.refreshToken(currentToken);
      const { token } = response.data;
      
      // Update token in storage
      localStorage.setItem(TOKEN_KEY, token);
      
      // Set up new refresh timer
      sessionService.setupTokenRefresh(token);
      
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      sessionService.clearSession();
      return false;
    }
  },
  
  /**
   * Verify if the current session is valid
   * @returns {Promise<boolean>} Validity status
   */
  verifySession: async () => {
    try {
      // Check if token exists
      const token = localStorage.getItem(TOKEN_KEY);
      
      if (!token) {
        return false;
      }
      
      // Call session check endpoint
      const response = await api.auth.checkSession();
      return response.data.valid === true;
    } catch (error) {
      console.error('Session verification failed:', error);
      return false;
    }
  },
  
  /**
   * Get the current authentication token
   * @returns {string|null} JWT token or null if not authenticated
   */
  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },
  
  /**
   * Set a new authentication token
   * @param {string} token - JWT token
   * @param {Function} onSessionWarning - Callback when session is about to expire
   */
  setToken: (token, onSessionWarning) => {
    localStorage.setItem(TOKEN_KEY, token);
    sessionService.setupTokenRefresh(token, onSessionWarning);
  },
  
  /**
   * Clear the current session
   */
  clearSession: () => {
    localStorage.removeItem(TOKEN_KEY);
    sessionService.clearTimers();
  },
  
  /**
   * Clear all session timers
   */
  clearTimers: () => {
    if (refreshTimer) {
      clearTimeout(refreshTimer);
      refreshTimer = null;
    }
    
    if (warningTimer) {
      clearTimeout(warningTimer);
      warningTimer = null;
    }
  },
  
  /**
   * Get user information from token
   * @returns {Object|null} User information or null if not authenticated
   */
  getUserFromToken: () => {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      
      if (!token) {
        return null;
      }
      
      const decoded = jwtDecode(token);
      
      return {
        id: decoded.sub,
        name: decoded.name,
        email: decoded.email
      };
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }
};

export default sessionService;