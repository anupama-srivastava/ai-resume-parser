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
  useTheme,
  useMediaQuery,
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
import toast from 'react-hot-toast';

const EnhancedDashboardFinal = () => {
  const theme = useTheme();
  const queryClient = useQueryClient();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateRange, setDateRange] = useState({ from: '', to: '' });
  const [selectedResumes, setSelectedResumes] = useState([]);
  const [bulkDialogOpen, setBulkDialogOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Enhanced dashboard stats with real-time updates
  const { data: stats, isLoading: statsLoading, refetch: refetchStats } = useQuery(
    'dashboard-stats',
    () => axios.get('/api/resumes/dashboard_stats/').then(res => res.data),
    {
      refetchInterval: 15000,
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

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await Promise.all([
      refetchStats(),
      queryClient.invalidateQueries('recent-resumes'),
    ]);
    setRefreshing(false);
    toast.success('Dashboard refreshed!');
  }, [refetchStats, queryClient]);

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
      <Box p={isMobile ? 2 : 3}>
        <Typography variant="h4" gutterBottom>
          <Skeleton width={200} />
        </Typography>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: isMobile ? 2 : 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant={isMobile ? 'h5' : 'h4'} fontWeight="bold">
          Dashboard
        </Typography>
        <IconButton onClick={handleRefresh} disabled={refreshing}>
          <RefreshIcon className={refreshing ? 'spinning' : ''} />
        </IconButton>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={isMobile ? 2 : 3} mb={3}>
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

      {/* Charts Section */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stats?.recent_activity?.resumes || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#1976d2" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              File Types
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats?.file_types || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ type, percent }) => `${type} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(stats?.file_types || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Search and Filters */}
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
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              type="date"
              label="From"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
              InputLabelProps={{ shrink: true }}
              size={isMobile ? 'small' : 'medium'}
            />
          </Grid>
          <Grid item xs={12} sm
