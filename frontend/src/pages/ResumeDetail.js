import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Work as WorkIcon,
  School as SchoolIcon,
  Code as CodeIcon,
  Language as LanguageIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from 'recharts';

const ResumeDetail = () => {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: resume, isLoading } = useQuery(
    ['resume', id],
    () => axios.get(`/api/resumes/${id}/`).then(res => res.data)
  );

  const { data: parsedResume } = useQuery(
    ['parsed-resume', id],
    () => axios.get(`/api/parsed-resumes/?resume=${id}`).then(res => res.data.results[0])
  );

  if (isLoading) {
    return <LinearProgress />;
  }

  if (!resume) {
    return <Typography>Resume not found</Typography>;
  }

  const skillsData = parsedResume?.skills?.technical?.map(skill => ({
    name: skill,
    value: 1,
  })) || [];

  const experienceData = parsedResume?.work_experience?.map(exp => ({
    company: exp.company,
    duration: exp.duration,
  })) || [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {resume.original_filename}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Parsed Information
            </Typography>

            {parsedResume && (
              <Box>
                <Typography variant="h5" gutterBottom>
                  {parsedResume.personal_info?.full_name || 'Name not found'}
                </Typography>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  {parsedResume.summary || 'No summary available'}
                </Typography>

                <Box mt={3}>
                  <Typography variant="h6" gutterBottom>
                    Work Experience
                  </Typography>
                  {parsedResume.work_experience?.map((exp, index) => (
                    <Card key={index} sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6">{exp.position}</Typography>
                        <Typography color="primary">{exp.company}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {exp.duration}
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {exp.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>

                <Box mt={3}>
                  <Typography variant="h6" gutterBottom>
                    Education
                  </Typography>
                  {parsedResume.education?.map((edu, index) => (
                    <Card key={index} sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6">{edu.degree}</Typography>
                        <Typography color="primary">{edu.institution}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {edu.graduation_year}
                        </Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>

                <Box mt={3}>
                  <Typography variant="h6" gutterBottom>
                    Projects
                  </Typography>
                  {parsedResume.projects?.map((project, index) => (
                    <Card key={index} sx={{ mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6">{project.name}</Typography>
                        <Typography variant="body2">{project.description}</Typography>
                        <Box sx={{ mt: 1 }}>
                          {project.technologies?.map((tech) => (
                            <Chip key={tech} label={tech} size="small" sx={{ mr: 1 }} />
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Skills Analysis
            </Typography>
            {parsedResume?.skills?.technical && (
              <Box>
                <Typography variant="body2" gutterBottom>
                  Technical Skills
                </Typography>
                {parsedResume.skills.technical.map((skill) => (
                  <Chip key={skill} label={skill} sx={{ mr: 1, mb: 1 }} />
                ))}
              </Box>
            )}
            {parsedResume?.skills?.soft && (
              <Box mt={2}>
                <Typography variant="body2" gutterBottom>
                  Soft Skills
                </Typography>
                {parsedResume.skills.soft.map((skill) => (
                  <Chip key={skill} label={skill} sx={{ mr: 1, mb: 1 }} />
                ))}
              </Box>
            )}
          </Paper>

          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Contact Information
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Email"
                  secondary={parsedResume?.personal_info?.email || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Phone"
                  secondary={parsedResume?.personal_info?.phone || 'Not provided'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Location"
                  secondary={parsedResume?.personal_info?.location || 'Not provided'}
                />
              </ListItem>
            </List>
          </Paper>

          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Processing Status
            </Typography>
            <Box display="flex" alignItems="center">
              <Typography variant="body2">
                Status: {resume.processing_status}
              </Typography>
              {resume.processing_status === 'completed' && (
                <Button
                  variant="contained"
                  color="primary"
                  size="small"
                  sx={{ ml: 2 }}
                  onClick={() => window.open(`/api/resumes/${id}/download/`, '_blank')}
                >
                  Download PDF
                </Button>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResumeDetail;
