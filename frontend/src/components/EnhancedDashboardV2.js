import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import axios from 'axios';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Paper,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Skeleton,
  Fade,
  Zoom,
  useTheme,
  useMediaQuery,
  Fab,
  SpeedDial,
  SpeedDialIcon,
  SpeedDialAction,
  Snackbar,
  Alert,
  Slide,
} from '@mui/material';
import {
  Description as ResumeIcon,
  Work as JobIcon,
  Assessment as MatchIcon,
  TrendingUp as TrendIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  CloudDownload as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  FileUpload as FileUploadIcon,
  Settings as SettingsIcon,
  Analytics as AnalyticsIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area,
} from 'recharts';
import { useTheme as useCustomTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

const EnhancedDashboardV2 = () => {
  const theme = useTheme();
  const queryClient = useQueryClient();
  const { isDarkMode, toggleDarkMode } = useCustomTheme();
  const { user } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateRange, setDateRange] = useState({ from: '', to: '' });
  const [selectedResumes, setSelectedResumes] = useState([]);
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [speedDialOpen, setSpeedDialOpen] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  // Enhanced dashboard stats with real-time updates
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useQuery(
    'dashboard-stats',
    () => axios.get('/api/resumes/dashboard_stats/').then(res => res.data),
    {
      refetchInterval: 15000, // Refresh every 15 seconds for real-time feel
      staleTime: 5000,
    }
  );

  // Enhanced recent resumes with advanced filtering
  const { data: recentResumes, isLoading: resumesLoading } = useQuery(
    ['recent-resumes', searchQuery, statusFilter, dateRange],
    () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (statusFilter) params.append('status', statusFilter);
      if (dateRange.from) params.append('date_from', dateRange.from);
      if (dateRange.to) params.append('date_to', dateRange.to);
      
      return axios.get(`/api/resumes/search/?${params.toString()}`).then(res => res.data);
    },
    {
      staleTime: 10000,
      keepPreviousData: true,
    }
  );

  // Real-time processing status updates
  useEffect(() => {
    const interval = setInterval(() => {
      const hasPending = recentResumes?.some(resume => resume.processing_status === 'pending');
      if (hasPending) {
        queryClient.invalidateQueries('recent-resumes');
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [recentResumes, queryClient]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await Promise.all([
      refetchStats(),
      queryClient.invalidateQueries('recent-resumes'),
    ]);
    setRefreshing(false);
    toast.success('Dashboard refreshed!', {
      icon: '🔄',
      duration: 2000,
    });
  }, [refetchStats, queryClient]);

  const handleBulkDelete = async () => {
    try {
      await Promise.all(
        selectedResumes.map(id => axios.delete(`/api/resumes/${id}/`))
      );
      setSelectedResumes([]);
      setBulkDialogOpen(false);
      queryClient.invalidateQueries('recent-resumes');
      toast.success(`${selectedResumes.length} resumes deleted successfully`, {
        icon: '🗑️',
      });
    } catch (error) {
      toast.error('Failed to delete resumes');
    }
  };

  const handleExport = async (format) => {
    try {
      const response = await axios.get('/api/resumes/export/', {
        params: { 
          format,
          ids: selectedResumes.length > 0 ? selectedResumes.join(',') : undefined
        },
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `resumes_${new Date().toISOString().split('T')[0]}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success(`Exported as ${format.toUpperCase()}`, {
        icon: '📊',
      });
    } catch (error) {
      toast.error('Export failed');
    }
  };

  // Enhanced stat cards with animations
  const StatCard = ({ title, value, icon, color, trend, loading }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ 
        height: '100%', 
        background: `linear-gradient(135deg, ${color}15, ${color}05)`,
        border: `1px solid ${color}20`,
      }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography color="textSecondary" gutterBottom variant="h6">
                {title}
              </Typography>
              {loading ? (
                <Skeleton variant="text" width={80} height={40} />
              ) : (
                <Typography variant="h4" component="div" fontWeight="bold">
                  {value}
                </Typography>
              )}
              {trend && (
                <Typography 
                  variant="body2" 
                  color={trend > 0 ? 'success.main' : 'error.main'}
                  fontWeight="medium"
                >
                  {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}% from last month
                </Typography>
              )}
            </Box>
            <Box 
              sx={{ 
                color: color, 
                opacity: 0.8,
                fontSize: '3rem',
              }}
            >
              {icon}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  // Enhanced processing status chip with better styling
  const ProcessingStatusChip = ({ status }) => {
    const statusConfig = {
      pending: { 
        label: 'Processing', 
        color: 'warning',
        icon: <CircularProgress size={16} sx={{ mr: 0.5 }} />
      },
      completed: { 
        label: 'Completed', 
        color: 'success',
        icon: <TrendIcon fontSize="small" sx={{ mr: 0.5 }} />
      },
      failed: { 
        label: 'Failed', 
        color: 'error',
        icon: <DeleteIcon fontSize="small" sx={{ mr: 0.5 }} />
      },
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    return (
      <Chip 
        label={config.label} 
        color={config.color} 
        size="small" 
        icon={config.icon}
        variant="outlined"
      />
    );
  };

  // Enhanced resume card with better mobile layout
  const ResumeCard = ({ resume }) => (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
    >
      <Card 
        sx={{ 
          height: '100%',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: (theme) => theme.shadows[8],
          },
        }}
      >
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
            <Typography 
              variant="h6" 
              noWrap 
              sx={{ 
                maxWidth: isMobile ? '150px' : '200px',
                fontWeight: 'bold'
              }}
            >
              {resume.original_filename}
            </Typography>
            <ProcessingStatusChip status={resume.processing_status} />
          </Box>
          
          <Typography variant="body2" color="textSecondary" gutterBottom>
            📅 {new Date(resume.created_at).toLocaleDateString()}
          </Typography>
          
          <Typography variant="body2" color="textSecondary" gutterBottom>
            📊 {(resume.file_size / 1024 / 1024).toFixed(2)} MB
          </Typography>
          
          <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
            <IconButton
              size="small"
              onClick={() => window.open(`/resumes/${resume.id}`, '_blank')}
              color="primary"
            >
              <ViewIcon />
            </IconButton>
            <Button
              size="small"
              variant="contained"
              href={`/resumes/${resume.id}`}
              sx={{ borderRadius: 2 }}
            >
              View Details
            </Button>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Loading skeleton for better UX
  if (statsLoading) {
    return (
      <Box p={isMobile ? 2 : 3}>
        <Grid container spacing={isMobile ? 2 : 3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  // Speed dial actions for mobile
  const actions = [
    { icon: <AddIcon />, name: 'Upload Resume', action: () => window.location.href = '/upload' },
    { icon: <FileUploadIcon />, name: 'Bulk Upload', action: () => window.location.href = '/bulk-upload' },
    { icon: <DownloadIcon />, name: 'Export Data', action: () => handleExport('csv') },
    { icon: isDarkMode ? <LightModeIcon /> : <DarkModeIcon />, name: 'Toggle Theme', action: toggleDarkMode },
  ];

  return (
    <Box sx={{ p: isMobile ? 2 : 3 }}>
      {/* Header with enhanced styling */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography variant={isMobile ? 'h5' : 'h4'} fontWeight="bold">
            Dashboard
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Welcome back, {user?.username || 'User'}! 👋
          </Typography>
        </motion.div>
        
        <Box>
          <IconButton 
            onClick={handleRefresh} 
            disabled={refreshing}
            sx={{ 
              animation: refreshing ? 'spin 1s linear infinite' : 'none',
              '@keyframes spin': {
                from: { transform: 'rotate(0deg)' },
                to: { transform: 'rotate(360deg)' },
              }
            }}
          >
            <RefreshIcon />
          </IconButton>
          <IconButton onClick={toggleDarkMode}>
            {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Box>
      </Box>

      {/* Enhanced Stats Cards */}
      <Grid container spacing={isMobile ? 2 : 3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Resumes"
            value={stats?.total_resumes || 0}
            icon={<ResumeIcon fontSize="large" />}
            color="#1976d2"
            trend={12}
            loading={statsLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Job Descriptions"
            value={stats?.total_jobs || 0}
            icon={<JobIcon fontSize="large" />}
            color="#388e3c"
            trend={8}
            loading={statsLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Match Results"
            value={stats?.total_matches || 0}
            icon={<MatchIcon fontSize="large" />}
            color="#f57c00"
            trend={-3}
            loading={statsLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${stats?.success_rate || 0}%`}
            icon={<TrendIcon fontSize="large" />}
            color="#7b1fa2"
            trend={5}
            loading={statsLoading}
          />
        </Grid>
      </Grid>

      {/* Enhanced Search and Filters */}
      <Paper elevation={2} sx={{ p: isMobile ? 2 : 3, mb: 3, borderRadius: 2 }}>
        <Grid container spacing={isMobile ? 1 : 2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search resumes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              size={isMobile ? 'small' : 'medium'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth size={isMobile ? 'small' : 'medium'}>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                label="Status"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="pending">Processing</MenuItem>
Let me continue with the implementation of the enhanced dashboard component. I will now proceed to create the `EnhancedDashboardV2.js` file.

<create_file>
<path>ai-resume-parser/frontend/src/components/EnhancedDashboardV2.js</path>
<content>
import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import axios from 'axios';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Paper,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Skeleton,
  Fade,
} from '@mui/material';
import {
  Description as ResumeIcon,
  Work as JobIcon,
  Assessment as MatchIcon,
  TrendingUp as TrendIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  CloudDownload as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import { useTheme } from '@mui/material/styles';
import toast from 'react-hot-toast';

const EnhancedDashboardV2 = () => {
  const theme = useTheme();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateRange, setDateRange] = useState({ from: '', to: '' });
  const [selectedResumes, setSelectedResumes] = useState([]);
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useQuery(
    'dashboard-stats',
    () => axios.get('/api/resumes/dashboard_stats/').then(res => res.data),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // Fetch recent resumes
  const { data: recentResumes, isLoading: resumesLoading } = useQuery(
    ['recent-resumes', searchQuery, statusFilter, dateRange],
    () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (statusFilter) params.append('status', statusFilter);
      if (dateRange.from) params.append('date_from', dateRange.from);
      if (dateRange.to) params.append('date_to', dateRange.to);
      
      return axios.get(`/api/resumes/search/?${params.toString()}`).then(res => res.data);
    },
    {
      staleTime: 10000,
    }
  );

  // Auto-refresh functionality
  useEffect(() => {
    const interval = setInterval(() => {
      queryClient.invalidateQueries('dashboard-stats');
    }, 30000);
    return () => clearInterval(interval);
  }, [queryClient]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([
      refetchStats(),
      queryClient.invalidateQueries('recent-resumes'),
    ]);
    setRefreshing(false);
    toast.success('Dashboard refreshed!');
  };

  const handleBulkDelete = async () => {
    try {
      await Promise.all(
        selectedResumes.map(id => axios.delete(`/api/resumes/${id}/`))
      );
      setSelectedResumes([]);
      setBulkDialogOpen(false);
      queryClient.invalidateQueries('recent-resumes');
      toast.success(`${selectedResumes.length} resumes deleted successfully`);
    } catch (error) {
      toast.error('Failed to delete resumes');
    }
  };

  const handleExport = async (format) => {
    try {
      const response = await axios.get('/api/resumes/export/', {
        params: { format },
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `resumes.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Export failed');
    }
  };

  const StatCard = ({ title, value, icon, color, trend }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
            {trend && (
              <Typography variant="body2" color={trend > 0 ? 'success.main' : 'error.main'}>
                {trend > 0 ? '+' : ''}{trend}% from last month
              </Typography>
            )}
          </Box>
          <Box color={color} sx={{ opacity: 0.8 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const ProcessingStatusChip = ({ status }) => {
    const statusConfig = {
      pending: { label: 'Processing', color: 'warning' },
      completed: { label: 'Completed', color: 'success' },
      failed: { label: 'Failed', color: 'error' },
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (statsLoading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          <Skeleton width={200} />
        </Typography>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rectangular" height={120} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Enhanced Dashboard
        </Typography>
        <Box>
          <IconButton onClick={handleRefresh} disabled={refreshing}>
            <RefreshIcon className={refreshing ? 'spinning' : ''} />
          </IconButton>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Resumes"
            value={stats?.total_resumes || 0}
            icon={<ResumeIcon fontSize="large" />}
            color="#1976d2"
            trend={12}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Job Descriptions"
            value={stats?.total_jobs || 0}
            icon={<JobIcon fontSize="large" />}
            color="#388e3c"
            trend={8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Match Results"
            value={stats?.total_matches || 0}
            icon={<MatchIcon fontSize="large" />}
            color="#f57c00"
            trend={-3}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${stats?.success_rate || 0}%`}
            icon={<TrendIcon fontSize="large" />}
            color="#7b1fa2"
            trend={5}
          />
        </Grid>
      </Grid>

      {/* Search and Filters */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search resumes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                label="Status"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="date"
              label="From"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="date"
              label="To"
              value={dateRange.to}
              onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => {
                setSearchQuery('');
                setStatusFilter('');
                setDateRange({ from: '', to: '' });
              }}
            >
              Clear
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Recent Resumes */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Recent Resumes
          </Typography>
          <Box>
            <Button
              startIcon={<DownloadIcon />}
              onClick={() => handleExport('csv')}
              sx={{ mr: 1 }}
            >
              Export CSV
            </Button>
            {selectedResumes.length > 0 && (
              <Button
                color="error"
                startIcon={<DeleteIcon />}
                onClick={() => setBulkDialogOpen(true)}
              >
                Delete ({selectedResumes.length})
              </Button>
            )}
          </Box>
        </Box>

        <Grid container spacing={2}>
          {resumesLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <Grid item xs={12} md={6} lg={4} key={i}>
                <Skeleton variant="rectangular" height={200} />
              </Grid>
            ))
          ) : (
            recentResumes?.map((resume) => (
              <Grid item xs={12} md={6} lg={4} key={resume.id}>
                <Fade in={true} timeout={500}>
                  <Card
                    sx={{
                      height: '100%',
                      transition: 'transform 0.2s',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 4,
                      },
                    }}
                  >
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                        <Typography variant="h6" noWrap>
                          {resume.original_filename}
                        </Typography>
                        <ProcessingStatusChip status={resume.processing_status} />
                      </Box>
                      
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Uploaded: {new Date(resume.created_at).toLocaleDateString()}
                      </Typography>
                      
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Size: {(resume.file_size / 1024 / 1024).toFixed(2)} MB
                      </Typography>
                      
                      <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                        <Box>
                          <IconButton
                            size="small"
                            onClick={() => window.open(`/resumes/${resume.id}`, '_blank')}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Box>
                        <Box>
                          <Button
                            size="small"
                            variant="outlined"
                            href={`/resumes/${resume.id}`}
                          >
                            View Details
                          </Button>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Fade>
              </Grid>
            ))
          )}
        </Grid>
      </Paper>

      {/* Bulk Delete Dialog */}
      <Dialog open={bulkDialogOpen} onClose={() => setBulkDialogOpen(false)}>
        <DialogTitle>Confirm Bulk Delete</DialogTitle>
        <DialogContent>
          Are you sure you want to delete {selectedResumes.length} resume(s)? This action cannot be undone.
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleBulkDelete} color="error">Delete</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedDashboardV2;
