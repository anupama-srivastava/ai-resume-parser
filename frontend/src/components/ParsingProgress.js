import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Fade,
  Zoom,
  Chip,
  IconButton,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  Refresh as RetryIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

const ParsingProgress = ({ resumeId, onComplete, onError }) => {
  const theme = useTheme();
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('pending');
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);
  const [startTime, setStartTime] = useState(null);

  const steps = [
    { label: 'Uploading file', description: 'Preparing your resume for processing' },
    { label: 'Extracting text', description: 'Reading content from your document' },
    { label: 'AI Analysis', description: 'Analyzing resume with advanced AI' },
    { label: 'Structuring data', description: 'Organizing extracted information' },
    { label: 'Finalizing', description: 'Completing the parsing process' },
  ];

  useEffect(() => {
    if (resumeId) {
      setStartTime(Date.now());
      startParsing();
    }
  }, [resumeId]);

  const startParsing = async () => {
    try {
      setStatus('processing');
      
      // Simulate progress for demo (in real app, use WebSocket/SSE)
      const interval = setInterval(() => {
        setProgress((prev) => {
          const newProgress = prev + Math.random() * 15;
          const step = Math.floor(newProgress / 20);
          
          if (step !== currentStep && step < steps.length) {
            setCurrentStep(step);
          }
          
          if (newProgress >= 100) {
            clearInterval(interval);
            setStatus('completed');
            setCurrentStep(steps.length - 1);
            if (onComplete) onComplete();
            return 100;
          }
          
          return newProgress;
        });
      }, 500);

      // In real implementation, use WebSocket or polling
      // const eventSource = new EventSource(`/api/resumes/${resumeId}/progress/`);
      // eventSource.onmessage = (event) => {
      //   const data = JSON.parse(event.data);
      //   setProgress(data.progress);
      //   setCurrentStep(data.step);
      //   setStatus(data.status);
      // };
      
      return () => clearInterval(interval);
    } catch (err) {
      setStatus('failed');
      setError(err.message);
      if (onError) onError(err);
    }
  };

  const handleRetry = () => {
    setProgress(0);
    setStatus('pending');
    setCurrentStep(0);
    setError(null);
    startParsing();
  };

  const getStepIcon = (stepIndex) => {
    if (stepIndex < currentStep) {
      return <CheckIcon color="success" />;
    } else if (stepIndex === currentStep) {
      if (status === 'failed') {
        return <ErrorIcon color="error" />;
      }
      return <PendingIcon color="primary" />;
    }
    return <PendingIcon color="disabled" />;
  };

  const getEstimatedTime = () => {
    if (!startTime) return 'Calculating...';
    const elapsed = Date.now() - startTime;
    const estimatedTotal = 15000; // 15 seconds estimated
    const remaining = Math.max(0, estimatedTotal - elapsed);
    
    if (remaining < 1000) return 'Almost done...';
    return `${Math.ceil(remaining / 1000)}s remaining`;
  };

  return (
    <Box>
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Resume Processing
            </Typography>
            <Chip
              label={status === 'completed' ? 'Complete' : 
                     status === 'failed' ? 'Failed' : 'Processing'}
              color={status === 'completed' ? 'success' : 
                     status === 'failed' ? 'error' : 'primary'}
              size="small"
            />
          </Box>

          {/* Progress Bar */}
          <Box mb={3}>
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body2" color="textSecondary">
                Progress
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {Math.round(progress)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 8,
                borderRadius: 4,
                [`& .MuiLinearProgress-bar`]: {
                  borderRadius: 4,
                },
              }}
            />
            <Typography variant="caption" color="textSecondary" mt={1} display="block">
              {getEstimatedTime()}
            </Typography>
          </Box>

          {/* Stepper */}
          <Stepper activeStep={currentStep} orientation="vertical" sx={{ mb: 3 }}>
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel
                  optional={
                    index === currentStep && status === 'processing' ? (
                      <Typography variant="caption">
                        {step.description}
                      </Typography>
                    ) : null
                  }
                  StepIconComponent={() => getStepIcon(index)}
                >
                  <Typography variant="body1">{step.label}</Typography>
                </StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Status Messages */}
          <Fade in={status !== 'processing'} timeout={600}>
            <Box>
              {status === 'completed' && (
                <Box display="flex" alignItems="center" color="success.main">
                  <CheckIcon sx={{ mr: 1 }} />
                  <Typography>Resume successfully parsed!</Typography>
                </Box>
              )}
              
              {status === 'failed' && (
                <Box>
                  <Box display="flex" alignItems="center" color="error.main" mb={2}>
                    <ErrorIcon sx={{ mr: 1 }} />
                    <Typography>Processing failed: {error || 'Unknown error'}</Typography>
                  </Box>
                  <Button
                    variant="outlined"
                    startIcon={<RetryIcon />}
                    onClick={handleRetry}
                    size="small"
                  >
                    Retry
                  </Button>
                </Box>
              )}
            </Box>
          </Fade>

          {/* Processing Details */}
          {status === 'processing' && (
            <Zoom in={true} timeout={500}>
              <Box
                sx={{
                  p: 2,
                  backgroundColor: theme.palette.grey[100],
                  borderRadius: 1,
                  mt: 2,
                }}
              >
                <Typography variant="body2" gutterBottom>
                  <strong>Current Step:</strong> {steps[currentStep]?.label}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {steps[currentStep]?.description}
                </Typography>
              </Box>
            </Zoom>
          )}
        </CardContent>
      </Card>

      {/* Mini Progress Indicator */}
      {status === 'processing' && (
        <Box
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            zIndex: 1000,
          }}
        >
          <Zoom in={true} timeout={300}>
            <Card sx={{ minWidth: 200 }}>
              <CardContent sx={{ p: 2 }}>
                <Box display="flex" alignItems="center">
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    Processing...
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={progress}
                  sx={{ mt: 1, height: 4 }}
                />
              </CardContent>
            </Card>
          </Zoom>
        </Box>
      )}
    </Box>
  );
};

// Hook for using parsing progress
export const useParsingProgress = () => {
  const [activeParsings, setActiveParsings] = useState({});

  const startParsing = (resumeId) => {
    setActiveParsings(prev => ({
      ...prev,
      [resumeId]: { status: 'pending', progress: 0 },
    }));
  };

  const updateProgress = (resumeId, data) => {
    setActiveParsings(prev => ({
      ...prev,
      [resumeId]: data,
    }));
  };

  const completeParsing = (resumeId) => {
    setActiveParsings(prev => {
      const newState = { ...prev };
      delete newState[resumeId];
      return newState;
    });
  };

  return {
    activeParsings,
    startParsing,
    updateProgress,
    completeParsing,
  };
};

export default ParsingProgress;
