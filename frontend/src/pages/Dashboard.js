import React, { useState } from 'react';
import EnhancedDashboard from '../components/EnhancedDashboard';
import ParsingProgress from '../components/ParsingProgress';

const Dashboard = () => {
  const [showParsingDemo, setShowParsingDemo] = useState(false);
  const [demoResumeId, setDemoResumeId] = useState(null);

  const handleParsingComplete = () => {
    console.log('Parsing completed!');
    setShowParsingDemo(false);
    setDemoResumeId(null);
  };

  const handleParsingError = (error) => {
    console.error('Parsing failed:', error);
  };

  return (
    <>
      <EnhancedDashboard />
      
      {/* Demo button for showing parsing progress */}
      {/* Remove this in production */}
      {/* <Button 
        variant="outlined" 
        onClick={() => {
          setDemoResumeId('demo-' + Date.now());
          setShowParsingDemo(true);
        }}
        sx={{ mt: 2 }}
      >
        Show Parsing Demo
      </Button> */}
      
      {showParsingDemo && (
        <ParsingProgress
          resumeId={demoResumeId}
          onComplete={handleParsingComplete}
          onError={handleParsingError}
        />
      )}
    </>
  );
};

export default Dashboard;
