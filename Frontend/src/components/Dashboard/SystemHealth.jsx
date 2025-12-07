import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    LinearProgress,
    Chip,
    IconButton,
    Tooltip,
    Alert,
    AlertTitle,
    Stack,
    Divider,
    Grid,
    Card,
    CardContent,
    CardHeader,
    Avatar,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Collapse,
    Button
} from '@mui/material';
import {
    Memory,
    Storage,
    NetworkCheck,
    Speed,
    Security,
    Error,
    Warning,
    CheckCircle,
    Refresh,
    ExpandMore,
    ExpandLess,
    Cpu,
    DeveloperBoard,
    Api,
    Cloud,
    Dns,
    Router
} from '@mui/icons-material';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { apiService } from '../../services/api';

const SystemHealth = ({ status, onRefresh }) => {
    const [expanded, setExpanded] = useState(false);
    const [healthData, setHealthData] = useState({
        cpu: 45,
        memory: 68,
        disk: 34,
        network: 92,
        latency: 120,
        errors: 2,
        uptime: '15d 6h 32m',
        lastIncident: '2024-01-10T14:32:00Z'
    });

    const [components, setComponents] = useState([
        { id: 'rag_engine', name: 'RAG Engine', status: 'healthy', latency: 45, icon: <Cpu /> },
        { id: 'vector_db', name: 'Vector Database', status: 'healthy', latency: 120, icon: <Storage /> },
        { id: 'llm_gateway', name: 'LLM Gateway', status: 'warning', latency: 320, icon: <Api /> },
        { id: 'action_engine', name: 'Action Engine', status: 'healthy', latency: 85, icon: <DeveloperBoard /> },
        { id: 'data_pipeline', name: 'Data Pipeline', status: 'healthy', latency: 60, icon: <Router /> },
        { id: 'websocket', name: 'WebSocket Server', status: 'error', latency: 1500, icon: <NetworkCheck /> }
    ]);

    const [incidents, setIncidents] = useState([
        { id: 1, component: 'WebSocket Server', time: '2 hours ago', status: 'resolved', description: 'Connection timeout' },
        { id: 2, component: 'LLM Gateway', time: '1 day ago', status: 'monitoring', description: 'High latency detected' },
        { id: 3, component: 'Vector Database', time: '3 days ago', status: 'resolved', description: 'Index optimization' }
    ]);

    const fetchHealth = async () => {
        try {
            const response = await apiService.getStatus();
            // Process response data here
            console.log('Health data:', response.data);
        } catch (error) {
            console.error('Failed to fetch health data:', error);
        }
    };

    useEffect(() => {
        fetchHealth();
        const interval = setInterval(fetchHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status) => {
        switch (status) {
            case 'healthy': return 'success';
            case 'warning': return 'warning';
            case 'error': return 'error';
            default: return 'default';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'healthy': return <CheckCircle />;
            case 'warning': return <Warning />;
            case 'error': return <Error />;
            default: return <CheckCircle />;
        }
    };

    const HealthMetric = ({ title, value, max = 100, unit = '%', icon, color, subtext }) => {
        const percentage = Math.min((value / max) * 100, 100);
        
        return (
            <Card>
                <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.dark`, mr: 2 }}>
                            {icon}
                        </Avatar>
                        <Box>
                            <Typography variant="body2" color="text.secondary">
                                {title}
                            </Typography>
                            <Typography variant="h6">
                                {value}{unit}
                            </Typography>
                        </Box>
                    </Box>
                    <LinearProgress 
                        variant="determinate" 
                        value={percentage} 
                        color={color}
                        sx={{ height: 8, borderRadius: 4 }}
                    />
                    {subtext && (
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                            {subtext}
                        </Typography>
                    )}
                </CardContent>
            </Card>
        );
    };

    const ComponentHealth = ({ component }) => (
        <ListItem
            sx={{
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                mb: 1,
                bgcolor: component.status === 'error' ? 'error.light' : 
                         component.status === 'warning' ? 'warning.light' : 
                         'success.light',
                opacity: component.status === 'error' ? 0.9 : 1
            }}
        >
            <ListItemIcon>
                <Box sx={{ color: `${getStatusColor(component.status)}.main` }}>
                    {component.icon}
                </Box>
            </ListItemIcon>
            <ListItemText
                primary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body1" fontWeight="medium">
                            {component.name}
                        </Typography>
                        <Chip
                            size="small"
                            icon={getStatusIcon(component.status)}
                            label={component.status.toUpperCase()}
                            color={getStatusColor(component.status)}
                            sx={{ color: 'white' }}
                        />
                    </Box>
                }
                secondary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                        <Typography variant="caption" color="text.secondary">
                            Latency: {component.latency}ms
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Updated: Just now
                        </Typography>
                    </Box>
                }
            />
        </ListItem>
    );

    return (
        <Box>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                    <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
                    System Health
                </Typography>
                <Box>
                    <Tooltip title="Refresh health data">
                        <IconButton onClick={onRefresh} size="small">
                            <Refresh />
                        </IconButton>
                    </Tooltip>
                    <Button
                        size="small"
                        endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
                        onClick={() => setExpanded(!expanded)}
                    >
                        {expanded ? 'Collapse' : 'Details'}
                    </Button>
                </Box>
            </Box>

            {/* Overall Status */}
            <Alert 
                severity={
                    components.some(c => c.status === 'error') ? 'error' :
                    components.some(c => c.status === 'warning') ? 'warning' : 'success'
                }
                sx={{ mb: 3 }}
            >
                <AlertTitle>
                    System Status: {
                        components.some(c => c.status === 'error') ? 'Degraded' :
                        components.some(c => c.status === 'warning') ? 'Attention Needed' : 'All Systems Operational'
                    }
                </AlertTitle>
                Uptime: {healthData.uptime} • Last incident: {healthData.lastIncident ? 'Resolved' : 'None'}
            </Alert>

            {/* Key Metrics */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} sm={3}>
                    <HealthMetric
                        title="CPU Usage"
                        value={healthData.cpu}
                        icon={<Cpu />}
                        color="primary"
                        subtext="2.4 GHz avg"
                    />
                </Grid>
                <Grid item xs={6} sm={3}>
                    <HealthMetric
                        title="Memory"
                        value={healthData.memory}
                        icon={<Memory />}
                        color="warning"
                        subtext="8GB/12GB used"
                    />
                </Grid>
                <Grid item xs={6} sm={3}>
                    <HealthMetric
                        title="Disk"
                        value={healthData.disk}
                        icon={<Storage />}
                        color="success"
                        subtext="342GB/1TB used"
                    />
                </Grid>
                <Grid item xs={6} sm={3}>
                    <HealthMetric
                        title="Network"
                        value={healthData.network}
                        icon={<NetworkCheck />}
                        color="info"
                        unit=" Mbps"
                        max={1000}
                        subtext="92% throughput"
                    />
                </Grid>
            </Grid>

            {/* Expanded Details */}
            <Collapse in={expanded}>
                <Stack spacing={3}>
                    {/* Component Health */}
                    <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Component Health
                        </Typography>
                        <List>
                            {components.map(component => (
                                <ComponentHealth key={component.id} component={component} />
                            ))}
                        </List>
                    </Paper>

                    {/* Recent Incidents */}
                    <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Recent Incidents
                        </Typography>
                        {incidents.map(incident => (
                            <Alert
                                key={incident.id}
                                severity={incident.status === 'resolved' ? 'success' : 'warning'}
                                sx={{ mb: 1 }}
                                icon={false}
                            >
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                                    <Box>
                                        <Typography fontWeight="medium">
                                            {incident.component}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {incident.description}
                                        </Typography>
                                    </Box>
                                    <Box sx={{ textAlign: 'right' }}>
                                        <Typography variant="caption" display="block">
                                            {incident.time}
                                        </Typography>
                                        <Chip
                                            size="small"
                                            label={incident.status}
                                            color={incident.status === 'resolved' ? 'success' : 'warning'}
                                            variant="outlined"
                                        />
                                    </Box>
                                </Box>
                            </Alert>
                        ))}
                    </Paper>

                    {/* Performance Indicators */}
                    <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Performance Indicators
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={6} md={3}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Box sx={{ width: 80, height: 80, margin: '0 auto' }}>
                                        <CircularProgressbar
                                            value={95}
                                            text={`${95}%`}
                                            styles={buildStyles({
                                                textColor: '#4caf50',
                                                pathColor: '#4caf50',
                                                trailColor: '#e0e0e0'
                                            })}
                                        />
                                    </Box>
                                    <Typography variant="caption" color="text.secondary">
                                        Query Success Rate
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={6} md={3}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Box sx={{ width: 80, height: 80, margin: '0 auto' }}>
                                        <CircularProgressbar
                                            value={healthData.latency > 500 ? 30 : 85}
                                            text={`${healthData.latency}ms`}
                                            styles={buildStyles({
                                                textColor: healthData.latency > 500 ? '#f44336' : '#1976d2',
                                                pathColor: healthData.latency > 500 ? '#f44336' : '#1976d2',
                                                trailColor: '#e0e0e0'
                                            })}
                                        />
                                    </Box>
                                    <Typography variant="caption" color="text.secondary">
                                        Average Latency
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={6} md={3}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Box sx={{ width: 80, height: 80, margin: '0 auto' }}>
                                        <CircularProgressbar
                                            value={98}
                                            text={`${98}%`}
                                            styles={buildStyles({
                                                textColor: '#ff9800',
                                                pathColor: '#ff9800',
                                                trailColor: '#e0e0e0'
                                            })}
                                        />
                                    </Box>
                                    <Typography variant="caption" color="text.secondary">
                                        Data Accuracy
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={6} md={3}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Box sx={{ width: 80, height: 80, margin: '0 auto' }}>
                                        <CircularProgressbar
                                            value={components.filter(c => c.status === 'healthy').length / components.length * 100}
                                            text={`${Math.round(components.filter(c => c.status === 'healthy').length / components.length * 100)}%`}
                                            styles={buildStyles({
                                                textColor: '#9c27b0',
                                                pathColor: '#9c27b0',
                                                trailColor: '#e0e0e0'
                                            })}
                                        />
                                    </Box>
                                    <Typography variant="caption" color="text.secondary">
                                        Service Availability
                                    </Typography>
                                </Box>
                            </Grid>
                        </Grid>
                    </Paper>
                </Stack>
            </Collapse>

            {/* Quick Stats */}
            {!expanded && (
                <Paper sx={{ p: 2, mt: 2 }}>
                    <Grid container spacing={2}>
                        <Grid item xs={4}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="h4" color="primary.main">
                                    {components.filter(c => c.status === 'healthy').length}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Healthy
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={4}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="h4" color="warning.main">
                                    {components.filter(c => c.status === 'warning').length}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Warnings
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={4}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="h4" color="error.main">
                                    {components.filter(c => c.status === 'error').length}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Errors
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>
                </Paper>
            )}
        </Box>
    );
};

export default SystemHealth;