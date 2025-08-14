import React from 'react';
import {
  VerticalTimeline,
  VerticalTimelineElement,
} from 'react-vertical-timeline-component';
import 'react-vertical-timeline-component/style.min.css';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { Work, TrendingUp, School } from '@mui/icons-material';

const CareerTrajectoryTimeline = ({ data }) => {
  if (!data) return null;

  const getIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'junior':
        return <Work />;
      case 'senior':
        return <TrendingUp />;
      case 'principal':
        return <School />;
      default:
        return <Work />;
    }
  };

  const getColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'junior':
        return '#4caf50';
      case 'mid-level':
        return '#ff9800';
      case 'senior':
        return '#f44336';
      case 'principal':
        return '#9c27b0';
      default:
        return '#2196f3';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Career Trajectory
        </Typography>
        <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
          <VerticalTimeline>
            {data.work_experiences?.map((exp, index) => (
              <VerticalTimelineElement
                key={index}
                className="vertical-timeline-element--work"
                contentStyle={{ background: getColor(exp.level), color: '#fff' }}
                contentArrowStyle={{ borderRight: `7px solid ${getColor(exp.level)}` }}
                date={exp.duration}
                iconStyle={{ background: getColor(exp.level), color: '#fff' }}
                icon={getIcon(exp.level)}
              >
                <h3 className="vertical-timeline-element-title">{exp.position}</h3>
                <h4 className="vertical-timeline-element-subtitle">{exp.company}</h4>
                <p>{exp.description}</p>
                <p>Skills: {exp.skills?.join(', ')}</p>
              </VerticalTimelineElement>
            ))}
          </VerticalTimeline>
        </Box>
        
        {data.future_predictions && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6">Future Predictions</Typography>
            {data.future_predictions.map((pred, index) => (
              <Box key={index} sx={{ mt: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                <Typography variant="body2">
                  <strong>{pred.predicted_role}</strong> - {pred.timeline}
                </Typography>
                <Typography variant="caption">
                  Required: {pred.required_skills?.join(', ')}
                </Typography>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default CareerTrajectoryTimeline;
