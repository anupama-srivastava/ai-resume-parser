import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ResumeUpload from './pages/ResumeUpload';
import ResumeDetail from './pages/ResumeDetail';
import JobDescriptions from './pages/JobDescriptions';
import Matching from './pages/Matching';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import Register from './pages/Register';
import AdvancedAnalyticsDashboard from './components/AdvancedAnalyticsDashboard';
import { AuthProvider } from './contexts/AuthContext';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<Layout />}>
                <Route index element={<Dashboard />} />
                <Route path="upload" element={<ResumeUpload />} />
                <Route path="resumes/:id" element={<ResumeDetail />} />
                <Route path="jobs" element={<JobDescriptions />} />
                <Route path="matching" element={<Matching />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="advanced-analytics" element={<AdvancedAnalyticsDashboard />} />
              </Route>
            </Routes>
          </Router>
        </AuthProvider>
        <Toaster position="top-right" />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
