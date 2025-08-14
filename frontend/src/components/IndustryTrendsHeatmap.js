import React, { useState } from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';

const IndustryTrendsHeatmap = ({ data }) => {
  const [selectedSkill, setSelectedSkill] = useState(null);

  if (!data) return null;

  const skillsColumns = [
    { field: 'skill', headerName: 'Skill', width: 150 },
    { field: 'count', headerName: 'Demand', width: 100 },
    { field: 'salary_premium', headerName: 'Salary Premium', width: 130 },
    { field: 'market_growth', headerName: 'Growth', width: 100 },
    {
      field: 'trend',
      headerName: 'Trend',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={params.value === 'increasing' ? 'success' : 'default'}
          size="small"
        />
      ),
    },
  ];

  const skillsRows = data.skills_trends?.map((trend, index) => ({
    id: index,
    skill: trend.skill,
    count: trend.count,
    salary_premium: `$${trend.salary_premium || 0}`,
    market_growth: `${(trend.market_growth * 100).toFixed(1)}%`,
    trend: trend.demand_trend,
  })) || [];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Industry Trends Heatmap
        </Typography>
        
        <Box sx={{ height: 400, width: '100%' }}>
          <DataGrid
            rows={skillsRows}
            columns={skillsColumns}
            pageSize={5}
            rowsPerPageOptions={[5, 10, 20]}
            checkboxSelection
            disableSelectionOnClick
            onSelectionModelChange={(newSelection) => {
              setSelectedSkill(newSelection[0]);
            }}
          />
        </Box>

        {data.emerging_technologies && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6">Emerging Technologies</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
              {data.emerging_technologies.map((tech, index) => (
                <Chip
                  key={index}
                  label={tech}
                  color="secondary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default IndustryTrendsHeatmap;
