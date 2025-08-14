import React, { useEffect, useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton,
  TextField,
  Button,
  Chip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Comment as CommentIcon,
  Share as ShareIcon,
  ThumbUp as ThumbUpIcon,
  Person as PersonIcon,
  Send as SendIcon
} from '@mui/icons-material';

const TeamCollaborationInterface = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { data: teamData, isLoading, error } = useQuery('team-collaboration', () =>
    axios.get('/api/v2/analytics/team_analytics/').then(res => res.data)
  );

  const [commentDialogOpen, setCommentDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [commentText, setCommentText] = useState('');

  if (isLoading) return <Typography>Loading team collaboration data...</Typography>;
  if (error) return <Typography>Error loading team collaboration data</Typography>;

  const handleComment = (item) => {
    setSelectedItem(item);
    setCommentDialogOpen(true);
  };

  const handleShare = (item) => {
    // Implement sharing logic
    console.log('Sharing item:', item);
  };

  const handleAddComment = () => {
    // Implement comment addition logic
    console.log('Adding comment:', commentText, 'to item:', selectedItem);
    setCommentDialogOpen(false);
    setCommentText('');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Team Collaboration Hub
      </Typography>
      
      <Grid container spacing={3}>
        {/* Team Overview */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Team Overview"
              subheader="Your collaborative workspace"
            />
            <CardContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <Typography variant="h6">Active Members</Typography>
                <Typography variant="h4" color="primary">
                  {teamData?.team_size || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Collaborating on {teamData?.total_resumes || 0} resumes
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Skills Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Skills Distribution"
              subheader="Team skill landscape"
            />
            <CardContent>
              <List dense>
                {Object.entries(teamData?.skills_distribution || {})
                  .slice(0, 5)
                  .map(([skill, count]) => (
                    <ListItem key={skill}>
                      <ListItemText
                        primary={skill}
                        secondary={`${count} members`}
                      />
                      <Chip label={count} size="small" color="primary" />
                    </ListItem>
                  ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Experience Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Experience Levels"
              subheader="Team experience breakdown"
            />
            <CardContent>
              <List dense>
                {Object.entries(teamData?.experience_distribution || {})
                  .map(([level, count]) => (
                    <ListItem key={level}>
                      <ListItemText
                        primary={level.charAt(0).toUpperCase() + level.slice(1)}
                        secondary={`${count} members`}
                      />
                      <Chip label={count} size="small" color="secondary" />
                    </ListItem>
                  ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Recent Activity"
              subheader="Latest team interactions"
            />
            <CardContent>
              <List>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar>
                      <PersonIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="John Doe shared a resume"
                    secondary="2 hours ago"
                  />
                  <IconButton onClick={() => handleComment('resume-1')}>
                    <CommentIcon />
                  </IconButton>
                  <IconButton onClick={() => handleShare('resume-1')}>
                    <ShareIcon />
                  </IconButton>
                </ListItem>
                
                <ListItem>
                  <ListItemAvatar>
                    <Avatar>
                      <PersonIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="Jane Smith added a comment"
                    secondary="1 day ago"
                  />
                  <IconButton onClick={() => handleComment('comment-1')}>
                    <CommentIcon />
                  </IconButton>
                  <IconButton onClick={() => handleShare('comment-1')}>
                    <ShareIcon />
                  </IconButton>
                </ListItem>
                
                <ListItem>
                  <ListItemAvatar>
                    <Avatar>
                      <PersonIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="Mike Johnson created a job match"
                    secondary="3 days ago"
                  />
                  <IconButton onClick={() => handleComment('match-1')}>
                    <CommentIcon />
                  </IconButton>
                  <IconButton onClick={() => handleShare('match-1')}>
                    <ShareIcon />
                  </IconButton>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Collaboration Metrics */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Collaboration Metrics"
              subheader="Team engagement statistics"
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {teamData?.collaboration_metrics?.total_comments || 0}
                    </Typography>
                    <Typography variant="body2">Total Comments</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {teamData?.collaboration_metrics?.active_collaborators || 0}
                    </Typography>
                    <Typography variant="body2">Active Collaborators</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {teamData?.collaboration_metrics?.recent_activity || 0}
                    </Typography>
                    <Typography variant="body2">Recent Activity</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary">
                      {teamData?.collaboration_metrics?.average_comments_per_item || 0}
                    </Typography>
                    <Typography variant="body2">Avg Comments/Item</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Comment Dialog */}
      <Dialog open={commentDialogOpen} onClose={() => setCommentDialogOpen(false)}>
        <DialogTitle>Add Comment</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Comment"
            type="text"
            fullWidth
            variant="outlined"
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            multiline
            rows={4}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCommentDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddComment} variant="contained">
            Add Comment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TeamCollaborationInterface;
