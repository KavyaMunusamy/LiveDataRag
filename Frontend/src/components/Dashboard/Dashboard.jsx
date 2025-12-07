import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Chip,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  CardHeader,
  IconButton
} from '@mui/material';
import {
  Timeline,
  TrendingUp,
  NotificationsActive,
  Security,
  Refresh,
  PlayArrow,
  Pause
} from '@mui/icons-material';
import DataStreams from './DataStreams';
import ActionLog from './ActionLog';
import SystemHealth from './SystemHealth';
import { useSystem } from '../../contexts/SystemContext';
import { api } from '../../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const { systemStatus, actions, dataStreams, toggleSystem, refreshData } = useSystem();
  const [liveStats, setLiveStats] = useState({
    totalQueries: 0,
    actionsExecuted: 0,
    dataPoints: 0,
    avgResponseTime: 0
  });

  useEffect(() => {
    // Fetch initial stats
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/v1/system/stats');
        setLiveStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Icon sx={{ color, mr: 1 }} />
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Live Data RAG with Actions
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Autonomous real-time data processing and action system
          </Typography>
        </Box>
        <Box>
          <IconButton
            onClick={toggleSystem}
            color={systemStatus.isActive ? 'secondary' : 'default'}
            sx={{ mr: 2 }}
          >
            {systemStatus.isActive ? <Pause /> : <PlayArrow />}
          </IconButton>
          <IconButton onClick={refreshData}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* System Status Alert */}
      <Alert
        severity={systemStatus.isActive ? 'success' : 'warning'}
        sx={{ mb: 3 }}
        action={
          <Chip
            label={systemStatus.isActive ? 'ACTIVE' : 'PAUSED'}
            color={systemStatus.isActive ? 'success' : 'warning'}
            size="small"
          />
        }
      >
        {systemStatus.isActive 
          ? 'System is actively monitoring data streams and processing queries'
          : 'System is paused. No actions will be executed.'}
        {systemStatus.lastAction && (
          <Typography variant="body2" sx={{ mt: 1 }}>
            Last action: {systemStatus.lastAction.type} at {new Date(systemStatus.lastAction.timestamp).toLocaleTimeString()}
          </Typography>
        )}
      </Alert>

      {/* Statistics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Queries"
            value={liveStats.totalQueries.toLocaleString()}
            icon={Timeline}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Actions Executed"
            value={liveStats.actionsExecuted.toLocaleString()}
            icon={NotificationsActive}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Data Points"
            value={liveStats.dataPoints.toLocaleString()}
            icon={TrendingUp}
            color="#388e3c"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Response"
            value={`${liveStats.avgResponseTime}ms`}
            icon={Security}
            color="#ed6c02"
          />
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Live Data Streams
            </Typography>
            <DataStreams streams={dataStreams} />
          </Paper>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              System Health
            </Typography>
            <SystemHealth status={systemStatus} />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <NotificationsActive sx={{ mr: 1 }} />
              <Typography variant="h6">Recent Actions</Typography>
            </Box>
            <ActionLog actions={actions.slice(0, 10)} />
          </Paper>
        </Grid>
      </Grid>

      {/* Real-time Updates Indicator */}
      {systemStatus.isActive && (
        <Box sx={{ position: 'fixed', bottom: 20, right: 20 }}>
          <Paper elevation={3} sx={{ p: 1, display: 'flex', alignItems: 'center' }}>
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                bgcolor: 'success.main',
                mr: 1,
                animation: 'pulse 1.5s infinite'
              }}
            />
            <Typography variant="caption">Live updates active</Typography>
          </Paper>
        </Box>
      )}
    </Container>
  );
};

export default Dashboard;