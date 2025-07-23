import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../utils/apiClient';
import sessionService from '../services/sessionService';

// Create context
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state from session service
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Get user from token
        const userFromToken = sessionService.getUserFromToken();
        
        if (userFromToken) {
          // Verify token with backend
          const isValid = await sessionService.verifySession();
          
          if (isValid) {
            // Set user state
            setUser({
              ...userFromToken,
              token: sessionService.getToken()
            });
          } else {
            // Token invalid, clear session
            sessionService.clearSession();
            setUser(null);
          }
        }
      } catch (err) {
        console.error('Auth initialization error:', err);
        sessionService.clearSession();
        setUser(null);
        setError('Session expired. Please log in again.');
      } finally {
        setLoading(false);
      }
    };

    // Initialize session service
    sessionService.init(
      // Session expired callback
      () => {
        setUser(null);
        setError('Session expired. Please log in again.');
      }
    );

    initializeAuth();
  }, []);

  // Handle Google login
  const handleGoogleLogin = async (credentialResponse) => {
    try {
      setLoading(true);
      setError(null);

      // Send token to backend for verification
      const response = await api.auth.login(credentialResponse.credential);

      // Store token using session service
      sessionService.setToken(response.data.token);

      // Set user state
      setUser({
        id: response.data.user.id,
        name: response.data.user.name,
        email: response.data.user.email,
        profilePicture: response.data.user.profile_picture,
        token: response.data.token
      });

      return true;
    } catch (err) {
      console.error('Google login error:', err);
      setError(err.response?.data?.error || 'Login failed. Please try again.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const logout = async () => {
    try {
      setLoading(true);
      
      // Call logout endpoint
      if (user?.token) {
        await api.auth.logout();
      }
      
      // Clear session and state
      sessionService.clearSession();
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
      // Still clear session and state on error
      sessionService.clearSession();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Refresh token
  const refreshToken = async () => {
    try {
      setLoading(true);
      
      // Use session service to refresh token
      const success = await sessionService.refreshToken();
      
      if (success) {
        // Update user state with new token
        const userFromToken = sessionService.getUserFromToken();
        setUser(prev => ({
          ...prev,
          ...userFromToken,
          token: sessionService.getToken()
        }));
      }
      
      return success;
    } catch (err) {
      console.error('Token refresh error:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Get user profile
  const getUserProfile = async () => {
    try {
      if (!user) return null;

      const response = await api.auth.getUser();
      return response.data.user;
    } catch (err) {
      console.error('Get user profile error:', err);
      return null;
    }
  };

  // Context value
  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    handleGoogleLogin,
    logout,
    refreshToken,
    getUserProfile,
    clearError: () => setError(null)
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;