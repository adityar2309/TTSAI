import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

// Initial state
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR',
  UPDATE_USER: 'UPDATE_USER'
};

// Reducer
function authReducer(state, action) {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null
      };
    
    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload.error
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      };
    
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };
    
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    
    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };
    
    default:
      return state;
  }
}

// Create context
const AuthContext = createContext();

// Auth provider component
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing token on app load
  useEffect(() => {
    const checkExistingAuth = () => {
      try {
        const token = localStorage.getItem('auth_token');
        
        if (token) {
          // Verify token is not expired
          const decodedToken = jwtDecode(token);
          const currentTime = Date.now() / 1000;
          
          if (decodedToken.exp > currentTime) {
            // Token is valid
            const user = {
              id: decodedToken.sub,
              name: decodedToken.name,
              email: decodedToken.email
            };
            
            dispatch({
              type: AUTH_ACTIONS.LOGIN_SUCCESS,
              payload: { user, token }
            });
          } else {
            // Token expired, remove it
            localStorage.removeItem('auth_token');
            dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
          }
        } else {
          dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        }
      } catch (error) {
        console.error('Error checking existing auth:', error);
        localStorage.removeItem('auth_token');
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      }
    };

    checkExistingAuth();
  }, []);

  // Auth actions
  const login = async (googleToken) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
      
      const response = await fetch(`${API_URL}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: googleToken }),
      });

      if (!response.ok) {
        throw new Error(`Authentication failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Store token in localStorage
      localStorage.setItem('auth_token', data.token);
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: {
          user: data.user,
          token: data.token
        }
      });

      return { success: true, user: data.user };
    } catch (error) {
      console.error('Login error:', error);
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: { error: error.message }
      });
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      // Remove token from localStorage
      localStorage.removeItem('auth_token');
      
      // Optional: Call backend logout endpoint
      if (state.token) {
        const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
        
        await fetch(`${API_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${state.token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  const updateUser = (userData) => {
    dispatch({
      type: AUTH_ACTIONS.UPDATE_USER,
      payload: userData
    });
  };

  const refreshToken = async () => {
    if (!state.token) return false;

    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
      
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${state.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('auth_token', data.token);
        
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: {
            user: state.user,
            token: data.token
          }
        });
        
        return true;
      }
    } catch (error) {
      console.error('Token refresh error:', error);
    }
    
    return false;
  };

  // Auto-refresh token before expiration
  useEffect(() => {
    if (!state.token || !state.isAuthenticated) return;

    const checkTokenExpiration = () => {
      try {
        const decodedToken = jwtDecode(state.token);
        const currentTime = Date.now() / 1000;
        const timeUntilExpiry = decodedToken.exp - currentTime;
        
        // Refresh token if it expires in less than 5 minutes
        if (timeUntilExpiry < 300) {
          refreshToken();
        }
      } catch (error) {
        console.error('Error checking token expiration:', error);
      }
    };

    // Check immediately
    checkTokenExpiration();
    
    // Check every minute
    const interval = setInterval(checkTokenExpiration, 60000);
    
    return () => clearInterval(interval);
  }, [state.token, state.isAuthenticated]);

  const value = {
    ...state,
    login,
    logout,
    clearError,
    updateUser,
    refreshToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export { AUTH_ACTIONS };