import React from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { Card, CardContent, Typography } from '@mui/material';

const SkillsGapChart = ({ data }) => {
  if (!data) return null;

  const chartData = Object.entries(data.skill_scores || {}).map(([skill, scores]) => ({
    skill,
    current: scores.relevance || 0,
    target: 1,
    demand: scores.demand / 100 || 0,
  }));

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Skills Gap Analysis
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={chartData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="skill" />
            <PolarRadiusAxis angle={90} domain={[0, 1]} />
            <Radar
              name="Current Level"
              dataKey="current"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.3}
            />
            <Radar
              name="Target Level"
              dataKey="target"
              stroke="#82ca9d"
              fill="#82ca9d"
              fillOpacity={0.3}
            />
            <Radar
              name="Market Demand"
              dataKey="demand"
              stroke="#ffc658"
              fill="#ffc658"
              fillOpacity={0.3}
            />
            <Tooltip />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
        <Typography variant="body2" color="text.secondary">
          Gap: {data.gap_percentage}% | Missing Skills: {data.missing_skills?.length || 0}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default SkillsGapChart;
