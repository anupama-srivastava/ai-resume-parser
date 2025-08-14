import React from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  Box,
  Typography,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import SkillsGapChart from './SkillsGapChart';
import CareerTrajectoryTimeline from './CareerTrajectoryTimeline';
import IndustryTrendsHeatmap from './IndustryTrendsHeatmap';
import SalaryInsightsChart from './SalaryInsightsChart';

const EnhancedDashboardComplete = () => {
  const { data, isLoading, error } = useQuery('comprehensive-analytics', () =>
    axios.get('/api/v2/analytics/comprehensive/').then(res => res.data)
  );

  if (isLoading) return <CircularProgress />;
  if (error) return <Typography color="error">Error loading analytics data</Typography>;

  const skillsGapData = data.skills_gap || {};
  const careerTrajectoryData = data.career_trajectory || {};
  const industryTrendsData = data.industry_trends || {};
  const salaryInsightsData = data.salary_insights || {};

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Advanced Analytics Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Skills Gap Analysis"
              subheader="Identify missing skills based on market trends"
            />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="h6">Current Skills</Typography>
                  <Chip label={`${Object.keys(skillsGapData.current_skills || {}).length} skills`} color="primary" />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="h6">Missing Skills</Typography>
                  <Chip label={`${(skillsGapData.missing_skills || []).length} skills`} color="secondary" />
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={skillsGapData.gap_percentage || 0} 
                  sx={{ height: 10, borderRadius: 5 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Gap: {skillsGapData.gap_percentage || 0}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Career Trajectory"
              subheader="Your career progression and future predictions"
            />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="h6">Current Level</Typography>
                  <Chip label={careerTrajectoryData.current_level || 'Unknown'} color="primary" />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="h6">Next Roles</Typography>
                  <Chip label={`${(careerTrajectoryData.next_roles || []).length} roles`} color="secondary" />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Experience: {careerTrajectoryData.current_experience || 0} years
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Industry Trends"
              subheader="Real-time market insights"
            />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Typography variant="h6">Trending Skills</Typography>
                <List dense>
                  {(industryTrendsData.skills_trends || []).slice(0, 5).map((skill, index) => (
                    <ListItem key={index}>
                      <ListItemText 
                        primary={skill.skill} 
                        secondary={`Demand: ${skill.demand}`}
                      />
                      <Chip label={`+${skill.growth_rate}%`} size="small" color="success" />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Salary Insights"
              subheader="Market value and compensation analysis"
            />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Typography variant="h6">Market Value</Typography>
                <Typography variant="h4" color="primary">
                  ${salaryInsightsData.market_value?.current_salary || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Potential: ${salaryInsightsData.market_value?.potential_salary || 0}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={salaryInsightsData.market_value?.growth_potential || 0} 
                  sx={{ height: 10, borderRadius: 5 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EnhancedDashboardComplete;
