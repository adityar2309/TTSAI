import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Layout from './components/Layout';
import Translator from './components/Translator';
import DiagnosticTool from './components/DiagnosticTool';
import { AuthProvider } from './contexts/AuthContext';
import { LoginPage } from './components/auth';
import AuthTest from './components/auth/AuthTest';
import { deepPurple, amber } from '@mui/material/colors';
import './styles/gradients.css';

function App() {
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem('themeMode');
    return savedMode || 'light';
  });

  const theme = useMemo(() => createTheme({
    palette: {
      mode,
      primary: {
        main: mode === 'dark' ? deepPurple[300] : deepPurple[500],
        light: mode === 'dark' ? deepPurple[200] : deepPurple[300],
        dark: mode === 'dark' ? deepPurple[400] : deepPurple[700],
      },
      secondary: {
        main: mode === 'dark' ? amber[300] : amber[500],
      },
      background: {
        default: mode === 'dark' ? '#121212' : '#f5f5f5',
        paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
      },
    },
    shape: {
      borderRadius: 12,
    },
    typography: {
      fontFamily: "'Inter', 'Roboto', 'Helvetica', 'Arial', sans-serif",
      h4: {
        fontSize: '1.75rem',
        fontWeight: 600,
        '@media (max-width:600px)': {
          fontSize: '1.5rem',
        },
      },
      h6: {
        fontSize: '1.25rem',
        fontWeight: 600,
        '@media (max-width:600px)': {
          fontSize: '1.1rem',
        },
      },
      body1: {
        fontSize: '1rem',
        '@media (max-width:600px)': {
          fontSize: '0.95rem',
        },
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
            '@media (max-width:600px)': {
              fontSize: '0.875rem',
              padding: '6px 16px',
            },
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            '@media (max-width:600px)': {
              padding: '8px',
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
    },
  }), [mode]);

  const toggleColorMode = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    localStorage.setItem('themeMode', newMode);
  };

  const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

  if (!googleClientId) {
    console.error('Google Client ID not found. Please set REACT_APP_GOOGLE_CLIENT_ID in your environment variables.');
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>
        <ThemeProvider theme={theme}>
          <Router>
            <Layout toggleColorMode={toggleColorMode} mode={mode}>
              <Routes>
                <Route path="/" element={<Translator />} />
                <Route path="/diagnostics" element={<DiagnosticTool />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/auth-test" element={<AuthTest />} />
              </Routes>
            </Layout>
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App; 