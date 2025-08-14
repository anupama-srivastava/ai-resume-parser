import React, { useEffect, useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  Box,
  Typography,
  CircularProgress,
  Grid,
} from '@mui/material';
import SkillsGapChart from './SkillsGapChart';
import CareerTrajectoryTimeline from './CareerTrajectoryTimeline';
import IndustryTrendsHeatmap from './IndustryTrendsHeatmap';
import SalaryInsightsChart from './SalaryInsightsChart';

const AdvancedAnalyticsDashboard = () => {
  const { data, isLoading, error } = useQuery('comprehensive-analytics', () =>
    axios.get('/api/analytics/comprehensive_analytics/').then(res => res.data)
  );

  if (isLoading) return <CircularProgress />;
  if (error) return <Typography color="error">Error loading analytics data</Typography>;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Advanced Analytics Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <SkillsGapChart data={data.skills_gap} />
        </Grid>
        <Grid item xs={12} md={6}>
          <CareerTrajectoryTimeline data={data.career_trajectory} />
        </Grid>
        <Grid item xs={12}>
          <IndustryTrendsHeatmap data={data.industry_trends} />
        </Grid>
        <Grid item xs={12}>
          <SalaryInsightsChart data={data.salary_insights} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdvancedAnalyticsDashboard;
