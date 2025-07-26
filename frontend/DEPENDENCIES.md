# Frontend Dependencies

This document outlines the dependencies installed for the Learning Tools Revamp project.

## Core Dependencies

### Already Installed
- **@react-oauth/google** (^0.12.1) - Google OAuth authentication for React
- **jwt-decode** (^4.0.0) - JWT token decoding for authentication
- **@mui/material** (^5.13.0) - Material-UI core components
- **@mui/icons-material** (^5.11.16) - Material-UI icons
- **@mui/lab** (^5.0.0-alpha.153) - Material-UI experimental components
- **axios** (^1.4.0) - HTTP client for API calls
- **react-router-dom** (^7.6.1) - Client-side routing

### Newly Added Dependencies

#### Form Handling & Validation
- **react-hook-form** (^7.61.1) - Performant forms with easy validation
- **@hookform/resolvers** (^5.2.0) - Validation resolvers for react-hook-form
- **yup** (^1.6.1) - Schema validation library

#### Data Management
- **@tanstack/react-query** (^5.83.0) - Data fetching and caching library
- **react-query** (^3.39.3) - Legacy version for compatibility

#### UI Enhancement & Animation
- **framer-motion** (^12.23.9) - Animation library for React
- **react-spring** (^10.0.1) - Spring-physics based animations
- **react-transition-group** (^4.4.5) - Transition components
- **react-countdown-circle-timer** (^3.2.1) - Circular countdown timer for quizzes

#### Data Visualization & Charts
- **@mui/x-charts** (^8.9.0) - Material-UI charts for progress visualization
- **recharts** (^3.1.0) - Composable charting library
- **@mui/x-data-grid** (^8.9.0) - Advanced data grid component

#### Date & Time
- **@mui/x-date-pickers** (^8.9.0) - Material-UI date/time pickers
- **date-fns** (^4.1.0) - Date utility library

#### Utilities
- **react-hotkeys-hook** (^5.1.0) - Keyboard shortcuts for React

## Development Dependencies

### Testing
- **@testing-library/jest-dom** (^6.6.3) - Custom Jest matchers for DOM testing
- **@testing-library/react** (^16.3.0) - React component testing utilities
- **@testing-library/user-event** (^14.6.1) - User interaction simulation for tests

## Purpose by Feature

### Google Authentication
- `@react-oauth/google` - Google sign-in button and OAuth flow
- `jwt-decode` - Decode JWT tokens from backend
- `react-hook-form` + `yup` - Form validation for auth forms

### Quiz Feature
- `react-hook-form` + `@hookform/resolvers` + `yup` - Quiz form handling and validation
- `react-countdown-circle-timer` - Quiz time limits
- `@mui/x-charts` + `recharts` - Quiz results visualization
- `framer-motion` - Quiz transition animations
- `react-hotkeys-hook` - Keyboard shortcuts for quiz navigation

### Learning Tools Page Redesign
- `@mui/x-data-grid` - Advanced data tables for progress tracking
- `@mui/x-charts` - Progress visualization
- `framer-motion` + `react-spring` - Card animations and transitions
- `react-transition-group` - Page transitions

### Avatar Chatbot
- `framer-motion` - Chat message animations
- `react-spring` - Smooth UI interactions
- `@tanstack/react-query` - Chat message caching and state management

### Cross-Feature Integration
- `@tanstack/react-query` - Global state management and data synchronization
- `@mui/x-date-pickers` - Date selection for progress tracking
- `date-fns` - Date formatting and manipulation

## Installation Commands Used

```bash
# Core packages for forms, data management, and UI
npm install @mui/x-data-grid @mui/x-date-pickers react-hook-form @hookform/resolvers yup react-query @tanstack/react-query react-transition-group framer-motion

# Additional UI and utility packages
npm install react-countdown-circle-timer react-spring @mui/x-charts recharts react-hotkeys-hook

# Testing utilities
npm install --save-dev @testing-library/jest-dom @testing-library/react @testing-library/user-event
```

## Notes

- Some peer dependency warnings are expected due to React version differences in sub-dependencies
- All packages are compatible with React 18.2.0
- Testing libraries are installed as dev dependencies to keep production bundle size minimal
- Material-UI X components require a license for production use beyond basic features