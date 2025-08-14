import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { Card, CardContent, Typography, Box } from '@mui/material';

const SalaryInsightsChart = ({ data }) => {
  if (!data) return null;

  const salaryData = data.salary_benchmarks?.map((benchmark) => ({
    level: benchmark.level,
    min: benchmark.min_salary,
    max: benchmark.max_salary,
    median: benchmark.median_salary,
  })) || [];

  const skillPremiumData = Object.entries(data.skill_premiums || {}).map(([skill, premium]) => ({
    skill,
    premium,
  }));

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Salary Insights
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Market Value: ${data.market_value?.current_market_value || 0}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Range: ${data.market_value?.potential_range?.min || 0} - ${data.market_value?.potential_range?.max || 0}
          </Typography>
        </Box>

        <Box sx={{ height: 300, mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Salary Benchmarks by Level
          </Typography>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={salaryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="level" />
              <YAxis />
              <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
              <Bar dataKey="min" fill="#8884d8" name="Min Salary" />
              <Bar dataKey="median" fill="#82ca9d" name="Median Salary" />
              <Bar dataKey="max" fill="#ffc658" name="Max Salary" />
            </BarChart>
          </ResponsiveContainer>
        </Box>

        <Box sx={{ height: 300 }}>
          <Typography variant="subtitle2" gutterBottom>
            Skill Premium Impact
          </Typography>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={skillPremiumData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="skill" />
              <YAxis />
              <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
              <Line type="monotone" dataKey="premium" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Box>

        {data.recommendations && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Recommendations
            </Typography>
            {data.recommendations.map((rec, index) => (
              <Typography key={index} variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                • {rec}
              </Typography>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default SalaryInsightsChart;
