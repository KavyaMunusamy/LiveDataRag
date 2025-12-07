import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    Card,
    CardContent,
    CardHeader,
    IconButton,
    Chip,
    LinearProgress,
    Tooltip,
    Switch,
    FormControlLabel,
    Menu,
    MenuItem,
    Divider,
    Badge,
    Avatar,
    Slider
} from '@mui/material';
import {
    Refresh,
    Pause,
    PlayArrow,
    Timeline,
    TrendingUp,
    TrendingDown,
    Equalizer,
    MoreVert,
    FilterList,
    Download,
    Warning,
    CheckCircle,
    Error,
    DataArray,
    BarChart,
    LineStyle
} from '@mui/icons-material';
import { LineChart, Line, BarChart as ReBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { format, subMinutes, parseISO } from 'date-fns';
import { LoadingSpinner, DataLoadingSpinner } from '../common/LoadingSpinner';
import './Dashboard.css';

const DataStreams = ({ streams = [], onRefresh, onToggleStream }) => {
    const [filter, setFilter] = useState('all');
    const [timeRange, setTimeRange] = useState('5m');
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [anchorEl, setAnchorEl] = useState(null);
    const [selectedStream, setSelectedStream] = useState(null);
    const [chartData, setChartData] = useState([]);

    const streamTypes = [
        { id: 'financial', name: 'Financial Data', color: '#1976d2', icon: <TrendingUp /> },
        { id: 'news', name: 'News Feeds', color: '#4caf50', icon: <Timeline /> },
        { id: 'social', name: 'Social Media', color: '#9c27b0', icon: <Equalizer /> },
        { id: 'sensor', name: 'IoT Sensors', color: '#ff9800', icon: <DataArray /> },
        { id: 'api', name: 'API Streams', color: '#f44336', icon: <BarChart /> }
    ];

    // Mock data for demonstration
    useEffect(() => {
        const generateChartData = () => {
            const data = [];
            const now = new Date();
            
            for (let i = 30; i >= 0; i--) {
                const time = subMinutes(now, i);
                data.push({
                    time: format(time, 'HH:mm'),
                    financial: Math.random() * 100 + 50,
                    news: Math.random() * 80 + 20,
                    social: Math.random() * 120 + 30,
                    sensor: Math.random() * 60 + 40,
                    api: Math.random() * 90 + 10
                });
            }
            return data;
        };

        setChartData(generateChartData());
        
        if (autoRefresh) {
            const interval = setInterval(() => {
                setChartData(prev => {
                    const newPoint = { ...prev[prev.length - 1] };
                    newPoint.time = format(new Date(), 'HH:mm');
                    newPoint.financial += (Math.random() - 0.5) * 10;
                    newPoint.news += (Math.random() - 0.5) * 8;
                    newPoint.social += (Math.random() - 0.5) * 12;
                    newPoint.sensor += (Math.random() - 0.5) * 6;
                    newPoint.api += (Math.random() - 0.5) * 9;
                    
                    return [...prev.slice(1), newPoint];
                });
            }, 5000);

            return () => clearInterval(interval);
        }
    }, [autoRefresh]);

    const filteredStreams = filter === 'all' 
        ? streams 
        : streams.filter(s => s.type === filter);

    const getStreamStatus = (stream) => {
        if (stream.error_rate > 0.1) return { status: 'error', label: 'High Errors' };
        if (stream.latency > 1000) return { status: 'warning', label: 'High Latency' };
        return { status: 'success', label: 'Healthy' };
    };

    const StreamCard = ({ stream }) => {
        const status = getStreamStatus(stream);
        
        return (
            <Card sx={{ height: '100%', transition: 'all 0.3s ease' }}>
                <CardHeader
                    avatar={
                        <Avatar sx={{ bgcolor: streamTypes.find(t => t.id === stream.type)?.color || '#1976d2' }}>
                            {streamTypes.find(t => t.id === stream.type)?.icon || <DataArray />}
                        </Avatar>
                    }
                    action={
                        <IconButton size="small" onClick={(e) => {
                            setSelectedStream(stream);
                            setAnchorEl(e.currentTarget);
                        }}>
                            <MoreVert />
                        </IconButton>
                    }
                    title={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1" noWrap>
                                {stream.name}
                            </Typography>
                            <Chip
                                size="small"
                                label={stream.active ? 'ACTIVE' : 'PAUSED'}
                                color={stream.active ? 'success' : 'default'}
                                variant="outlined"
                            />
                        </Box>
                    }
                    subheader={`${stream.data_points?.toLocaleString() || 0} data points`}
                />
                <CardContent>
                    <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                                Status
                            </Typography>
                            <Chip
                                size="small"
                                icon={status.status === 'success' ? <CheckCircle /> : 
                                      status.status === 'warning' ? <Warning /> : <Error />}
                                label={status.label}
                                color={status.status}
                                variant="filled"
                                sx={{ color: 'white' }}
                            />
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                                Latency
                            </Typography>
                            <Typography variant="caption" fontWeight="bold">
                                {stream.latency || 0}ms
                            </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                                Error Rate
                            </Typography>
                            <Typography variant="caption" fontWeight="bold" color={stream.error_rate > 0.05 ? 'error.main' : 'success.main'}>
                                {(stream.error_rate * 100 || 0).toFixed(1)}%
                            </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="caption" color="text.secondary">
                                Throughput
                            </Typography>
                            <Typography variant="caption" fontWeight="bold">
                                {stream.throughput || 0}/s
                            </Typography>
                        </Box>
                    </Box>
                    
                    <LinearProgress 
                        variant="determinate" 
                        value={stream.throughput || 0} 
                        sx={{ height: 4, borderRadius: 2, mb: 1 }}
                    />
                    
                    <Typography variant="caption" color="text.secondary">
                        Last updated: {format(parseISO(stream.last_updated || new Date().toISOString()), 'HH:mm:ss')}
                    </Typography>
                </CardContent>
            </Card>
        );
    };

    const StreamMenu = () => (
        <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
        >
            <MenuItem onClick={() => {
                onToggleStream?.(selectedStream.id);
                setAnchorEl(null);
            }}>
                {selectedStream?.active ? <Pause sx={{ mr: 1 }} /> : <PlayArrow sx={{ mr: 1 }} />}
                {selectedStream?.active ? 'Pause Stream' : 'Resume Stream'}
            </MenuItem>
            <MenuItem onClick={() => {
                console.log('Configure stream:', selectedStream);
                setAnchorEl(null);
            }}>
                <FilterList sx={{ mr: 1 }} />
                Configure Filters
            </MenuItem>
            <MenuItem onClick={() => {
                console.log('Export stream data:', selectedStream);
                setAnchorEl(null);
            }}>
                <Download sx={{ mr: 1 }} />
                Export Data
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => setAnchorEl(null)}>
                <Error sx={{ mr: 1 }} />
                View Error Logs
            </MenuItem>
        </Menu>
    );

    if (streams.length === 0) {
        return (
            <Box sx={{ textAlign: 'center', py: 8 }}>
                <DataLoadingSpinner 
                    message="Waiting for data streams..." 
                    subMessage="Data will appear when sources are connected"
                />
            </Box>
        );
    }

    return (
        <Box>
            {/* Controls */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                            <Chip
                                icon={<FilterList />}
                                label="Filters"
                                variant="outlined"
                                onClick={() => setFilter(filter === 'all' ? 'financial' : 'all')}
                            />
                            <Slider
                                size="small"
                                value={timeRange === '5m' ? 5 : timeRange === '15m' ? 15 : 30}
                                min={5}
                                max={30}
                                step={5}
                                marks={[
                                    { value: 5, label: '5m' },
                                    { value: 15, label: '15m' },
                                    { value: 30, label: '30m' }
                                ]}
                                valueLabelDisplay="auto"
                                valueLabelFormat={(value) => `${value}m`}
                                onChange={(e, value) => setTimeRange(`${value}m`)}
                                sx={{ width: 200 }}
                            />
                        </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={autoRefresh}
                                        onChange={(e) => setAutoRefresh(e.target.checked)}
                                        size="small"
                                    />
                                }
                                label="Auto-refresh"
                                labelPlacement="start"
                            />
                            <Tooltip title="Refresh streams">
                                <IconButton onClick={onRefresh} size="small">
                                    <Refresh />
                                </IconButton>
                            </Tooltip>
                        </Box>
                    </Grid>
                </Grid>
            </Paper>

            {/* Stats Summary */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                {streamTypes.map(type => {
                    const count = streams.filter(s => s.type === type.id).length;
                    const active = streams.filter(s => s.type === type.id && s.active).length;
                    
                    return (
                        <Grid item xs={6} sm={4} md={2.4} key={type.id}>
                            <Card sx={{ textAlign: 'center', p: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                                    <Box sx={{ color: type.color }}>
                                        {type.icon}
                                    </Box>
                                    <Box>
                                        <Typography variant="h6">{count}</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            {type.name}
                                        </Typography>
                                        <Typography variant="caption" display="block" color={active === count ? 'success.main' : 'warning.main'}>
                                            {active}/{count} active
                                        </Typography>
                                    </Box>
                                </Box>
                            </Card>
                        </Grid>
                    );
                })}
            </Grid>

            {/* Real-time Chart */}
            <Paper sx={{ p: 2, mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                        <LineStyle sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Real-time Data Flow
                    </Typography>
                    <Chip
                        size="small"
                        icon={autoRefresh ? <PlayArrow /> : <Pause />}
                        label={autoRefresh ? 'Live' : 'Paused'}
                        color={autoRefresh ? 'success' : 'default'}
                    />
                </Box>
                <Box sx={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="time" />
                            <YAxis />
                            <RechartsTooltip />
                            <Area type="monotone" dataKey="financial" stackId="1" stroke="#1976d2" fill="#1976d2" fillOpacity={0.6} />
                            <Area type="monotone" dataKey="news" stackId="1" stroke="#4caf50" fill="#4caf50" fillOpacity={0.6} />
                            <Area type="monotone" dataKey="social" stackId="1" stroke="#9c27b0" fill="#9c27b0" fillOpacity={0.6} />
                            <Area type="monotone" dataKey="sensor" stackId="1" stroke="#ff9800" fill="#ff9800" fillOpacity={0.6} />
                            <Area type="monotone" dataKey="api" stackId="1" stroke="#f44336" fill="#f44336" fillOpacity={0.6} />
                        </AreaChart>
                    </ResponsiveContainer>
                </Box>
            </Paper>

            {/* Stream Cards */}
            <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                Active Streams ({filteredStreams.length})
            </Typography>
            
            {filteredStreams.length === 0 ? (
                <Paper sx={{ p: 4, textAlign: 'center' }}>
                    <Typography color="text.secondary">
                        No streams match the current filter
                    </Typography>
                </Paper>
            ) : (
                <Grid container spacing={2}>
                    {filteredStreams.map((stream, index) => (
                        <Grid item xs={12} sm={6} md={4} key={stream.id || index}>
                            <StreamCard stream={stream} />
                        </Grid>
                    ))}
                </Grid>
            )}

            <StreamMenu />
        </Box>
    );
};

export default DataStreams;