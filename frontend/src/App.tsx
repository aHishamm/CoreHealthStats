import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box
} from '@mui/material';
import { BrowserRouter as Router } from 'react-router-dom';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import NavigationBar from './components/layout/NavigationBar';
import Sidebar from './components/layout/Sidebar';
import DashboardView from './components/dashboard/DashboardView';
import WorkoutView from './components/dashboard/WorkoutView';
import UploadView from './components/dashboard/UploadView';
import { useAuth } from './hooks/useHealthData';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  // const { isAuthenticated } = useAuth(); // Commented out for now
  const isAuthenticated = true; // Temporarily bypass authentication

  const handleLoginSuccess = () => {
    // Authentication state will be updated automatically
    setCurrentView('dashboard');
  };

  const handleRegisterSuccess = () => {
    setAuthMode('login');
  };

  const handleLogout = () => {
    setCurrentView('dashboard');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <DashboardView />;
      case 'workouts':
        return <WorkoutView />;
      case 'daily-metrics':
        return <div>Daily Metrics View (Coming Soon)</div>;
      case 'sleep':
        return <div>Sleep View (Coming Soon)</div>;
      case 'analytics':
        return <div>Analytics View (Coming Soon)</div>;
      case 'upload':
        return <UploadView />;
      case 'profile':
        return <div>Profile View (Coming Soon)</div>;
      case 'settings':
        return <div>Settings View (Coming Soon)</div>;
      default:
        return <DashboardView />;
    }
  };

  // Temporarily commented out authentication check
  /*
  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          {authMode === 'login' ? (
            <LoginForm
              onLoginSuccess={handleLoginSuccess}
              onSwitchToRegister={() => setAuthMode('register')}
            />
          ) : (
            <RegisterForm
              onRegisterSuccess={handleRegisterSuccess}
              onSwitchToLogin={() => setAuthMode('login')}
            />
          )}
        </Router>
      </ThemeProvider>
    );
  }
  */

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <NavigationBar onLogout={handleLogout} />
          <Sidebar activeView={currentView} onViewChange={setCurrentView} />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              ml: '240px', // Sidebar width
              mt: '64px', // AppBar height
              backgroundColor: '#f5f5f5',
              minHeight: 'calc(100vh - 64px)',
            }}
          >
            {renderCurrentView()}
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
