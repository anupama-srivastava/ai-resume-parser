import React, { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Work as WorkIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const JobDescriptions = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    skills_required: [],
    experience_required: '',
  });

  const { data: jobDescriptions, isLoading } = useQuery(
    'job-descriptions',
    () => axios.get('/api/job-descriptions/').then(res => res.data.results)
  );

  const handleCreate = async () => {
    try {
      const response = await axios.post('/api/job-descriptions/', formData);
      toast.success('Job description created successfully!');
      setOpenDialog(false);
    } catch (error) {
      toast.error('Failed to create job description');
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Job Descriptions
      </Typography>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">
          Total: {jobDescriptions?.length || 0} job descriptions
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create New
        </Button>
      </Box>

      <Grid container spacing={3}>
        {jobDescriptions?.map((job) => (
          <Grid item xs={12} sm={6} md={4} key={job.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {job.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" noWrap>
                  {job.description}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Skills: {job.skills_required?.join(', ') || 'Not specified'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Experience: {job.experience_required || 'Not specified'}
                  </Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  {job.skills_required?.map((skill) => (
                    <Chip key={skill} label={skill} size="small" sx={{ mr: 1, mb: 1 }} />
                  ))}
                </Box>
              </CardContent>
              <CardActions>
                <Button size="small" color="primary" onClick={() => navigate(`/jobs/${job.id}`)}>
                  View Details
                </Button>
                <Button size="small" color="secondary">
                  Edit
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default JobDescriptions;
