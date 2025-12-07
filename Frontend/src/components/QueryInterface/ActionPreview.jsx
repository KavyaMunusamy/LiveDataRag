import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    Chip,
    Alert,
    AlertTitle,
    Stack,
    Divider,
    Card,
    CardContent,
    CardActions,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Collapse,
    IconButton,
    LinearProgress,
    Tooltip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControlLabel,
    Switch,
    Grid
} from '@mui/material';
import {
    PlayArrow,
    Pause,
    Warning,
    CheckCircle,
    Error,
    Info,
    Schedule,
    Lock,
    LockOpen,
    Visibility,
    VisibilityOff,
    History,
    Timeline,
    Security,
    Code,
    DataArray,
    ArrowForward,
    Cancel,
    DoneAll,
    Help,
    Settings
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { format, parseISO } from 'date-fns';

const ActionPreview = ({ 
    action = null, 
    onConfirm, 
    onReject, 
    onConfigure,
    autoConfirm = false
}) => {
    const [expanded, setExpanded] = useState(false);
    const [showConfig, setShowConfig] = useState(false);
    const [config, setConfig] = useState({});
    const [countdown, setCountdown] = useState(30);

    if (!action) {
        return (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Action Required
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    The system is monitoring data. Actions will appear here when needed.
                </Typography>
            </Paper>
        );
    }

    const {
        action_type,
        action_parameters,
        reason,
        confidence,
        urgency_score,
        expected_impact,
        requires_confirmation = true,
        timestamp
    } = action;

    const getActionIcon = (type) => {
        switch (type) {
            case 'alert': return <Warning />;
            case 'api_call': return <Code />;
            case 'data_update': return <DataArray />;
            case 'workflow_trigger': return <Timeline />;
            default: return <Info />;
        }
    };

    const getActionColor = (type) => {
        switch (type) {
            case 'alert': return 'warning';
            case 'api_call': return 'primary';
            case 'data_update': return 'success';
            case 'workflow_trigger': return 'info';
            default: return 'default';
        }
    };

    const getImpactColor = (impact) => {
        switch (impact?.toLowerCase()) {
            case 'high': return 'error';
            case 'medium': return 'warning';
            case 'low': return 'success';
            default: return 'info';
        }
    };

    const getConfidenceLevel = (confidence) => {
        if (confidence >= 0.9) return { color: 'success', label: 'Very High' };
        if (confidence >= 0.7) return { color: 'success', label: 'High' };
        if (confidence >= 0.5) return { color: 'warning', label: 'Medium' };
        return { color: 'error', label: 'Low' };
    };

    // Countdown timer for auto-confirm
    React.useEffect(() => {
        if (autoConfirm && requires_confirmation && countdown > 0) {
            const timer = setTimeout(() => {
                setCountdown(prev => prev - 1);
                if (countdown === 1) {
                    onConfirm?.(action);
                }
            }, 1000);
            return () => clearTimeout(timer);
        }
    }, [autoConfirm, countdown, requires_confirmation]);

    const ActionDetailCard = ({ title, icon, children, color = 'primary' }) => (
        <Card variant="outlined" sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Box sx={{ color: `${color}.main` }}>
                        {icon}
                    </Box>
                    <Typography variant="subtitle2" color="text.secondary">
                        {title}
                    </Typography>
                </Box>
                {children}
            </CardContent>
        </Card>
    );

    return (
        <>
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
            >
                <Paper sx={{ p: 3 }}>
                    {/* Header */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ bgcolor: `${getActionColor(action_type)}.main` }}>
                                {getActionIcon(action_type)}
                            </Avatar>
                            <Box>
                                <Typography variant="h5" fontWeight="medium">
                                    {action_type?.replace('_', ' ').toUpperCase()} Action
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Requires {requires_confirmation ? 'Confirmation' : 'Automatic Execution'}
                                </Typography>
                            </Box>
                        </Box>
                        <Stack direction="row" spacing={1}>
                            <Tooltip title="Configure action">
                                <IconButton onClick={() => setShowConfig(true)}>
                                    <Settings />
                                </IconButton>
                            </Tooltip>
                            <Tooltip title={expanded ? 'Collapse details' : 'Expand details'}>
                                <IconButton onClick={() => setExpanded(!expanded)}>
                                    {expanded ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            </Tooltip>
                        </Stack>
                    </Box>

                    {/* Action Summary */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <ActionDetailCard 
                                title="Confidence Level" 
                                icon={<Security />}
                                color={getConfidenceLevel(confidence).color}
                            >
                                <Typography variant="h4" color={`${getConfidenceLevel(confidence).color}.main`}>
                                    {(confidence * 100).toFixed(0)}%
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {getConfidenceLevel(confidence).label} confidence
                                </Typography>
                            </ActionDetailCard>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                            <ActionDetailCard 
                                title="Urgency" 
                                icon={<Schedule />}
                                color={urgency_score >= 7 ? 'error' : urgency_score >= 4 ? 'warning' : 'success'}
                            >
                                <Typography variant="h4">
                                    {urgency_score || 'N/A'}/10
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {urgency_score >= 7 ? 'Critical' : urgency_score >= 4 ? 'Moderate' : 'Low'} urgency
                                </Typography>
                            </ActionDetailCard>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                            <ActionDetailCard 
                                title="Expected Impact" 
                                icon={<Timeline />}
                                color={getImpactColor(expected_impact)}
                            >
                                <Typography variant="h4" textTransform="uppercase" color={`${getImpactColor(expected_impact)}.main`}>
                                    {expected_impact || 'Unknown'}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Potential impact level
                                </Typography>
                            </ActionDetailCard>
                        </Grid>
                        
                        <Grid item xs={12} sm={6} md={3}>
                            <ActionDetailCard 
                                title="Safety Level" 
                                icon={requires_confirmation ? <Lock /> : <LockOpen />}
                                color={requires_confirmation ? 'warning' : 'success'}
                            >
                                <Typography variant="h4">
                                    {requires_confirmation ? 'High' : 'Auto'}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {requires_confirmation ? 'Manual confirmation' : 'Autonomous'}
                                </Typography>
                            </ActionDetailCard>
                        </Grid>
                    </Grid>

                    {/* Reason and Description */}
                    <Alert 
                        severity="info" 
                        sx={{ mb: 3 }}
                        action={
                            <Button 
                                size="small" 
                                startIcon={<Help />}
                                onClick={() => console.log('Show more info')}
                            >
                                Learn More
                            </Button>
                        }
                    >
                        <AlertTitle>Action Reasoning</AlertTitle>
                        {reason || 'No specific reason provided for this action.'}
                    </Alert>

                    {/* Expanded Details */}
                    <Collapse in={expanded}>
                        <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Action Details
                            </Typography>
                            <Divider sx={{ mb: 2 }} />
                            
                            <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                        Parameters
                                    </Typography>
                                    <Paper 
                                        variant="outlined" 
                                        sx={{ 
                                            p: 2, 
                                            bgcolor: 'grey.50',
                                            fontFamily: 'monospace',
                                            fontSize: '0.875rem',
                                            maxHeight: 200,
                                            overflow: 'auto'
                                        }}
                                    >
                                        <pre style={{ margin: 0 }}>
                                            {JSON.stringify(action_parameters || {}, null, 2)}
                                        </pre>
                                    </Paper>
                                </Grid>
                                
                                <Grid item xs={12} md={6}>
                                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                        System Context
                                    </Typography>
                                    <List dense>
                                        <ListItem>
                                            <ListItemIcon>
                                                <History />
                                            </ListItemIcon>
                                            <ListItemText 
                                                primary="Generated" 
                                                secondary={timestamp ? format(parseISO(timestamp), 'PPpp') : 'Just now'}
                                            />
                                        </ListItem>
                                        <ListItem>
                                            <ListItemIcon>
                                                <DataArray />
                                            </ListItemIcon>
                                            <ListItemText 
                                                primary="Data Sources" 
                                                secondary="Real-time financial, news, and market data"
                                            />
                                        </ListItem>
                                        <ListItem>
                                            <ListItemIcon>
                                                <Security />
                                            </ListItemIcon>
                                            <ListItemText 
                                                primary="Safety Checks" 
                                                secondary="All safety protocols passed"
                                            />
                                        </ListItem>
                                    </List>
                                </Grid>
                            </Grid>
                        </Paper>
                    </Collapse>

                    {/* Auto-confirm Countdown */}
                    {autoConfirm && requires_confirmation && (
                        <Alert severity="warning" sx={{ mb: 2 }}>
                            <AlertTitle>Auto-confirm in {countdown} seconds</AlertTitle>
                            Action will be automatically confirmed if no manual intervention.
                            <LinearProgress 
                                variant="determinate" 
                                value={(countdown / 30) * 100} 
                                sx={{ mt: 1, height: 4 }}
                            />
                        </Alert>
                    )}

                    {/* Action Buttons */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 3 }}>
                        <Stack direction="row" spacing={1}>
                            <Button
                                size="small"
                                startIcon={<Info />}
                                onClick={() => console.log('Show audit log')}
                                variant="text"
                            >
                                View Audit Trail
                            </Button>
                            <Button
                                size="small"
                                startIcon={<History />}
                                onClick={() => console.log('Show similar actions')}
                                variant="text"
                            >
                                Similar Actions
                            </Button>
                        </Stack>
                        
                        <Stack direction="row" spacing={2}>
                            <Button
                                variant="outlined"
                                color="error"
                                startIcon={<Cancel />}
                                onClick={() => onReject?.(action)}
                                size="large"
                            >
                                Reject
                            </Button>
                            <Button
                                variant="contained"
                                color="primary"
                                startIcon={<DoneAll />}
                                onClick={() => onConfirm?.(action)}
                                size="large"
                                autoFocus
                            >
                                Confirm & Execute
                            </Button>
                        </Stack>
                    </Box>
                </Paper>
            </motion.div>

            {/* Configuration Dialog */}
            <Dialog 
                open={showConfig} 
                onClose={() => setShowConfig(false)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Settings />
                        Configure Action
                    </Box>
                </DialogTitle>
                <DialogContent>
                    <Stack spacing={3} sx={{ mt: 2 }}>
                        <TextField
                            label="Action Name"
                            defaultValue={`${action_type}_${Date.now()}`}
                            fullWidth
                        />
                        
                        <FormControlLabel
                            control={
                                <Switch
                                    defaultChecked={requires_confirmation}
                                    onChange={(e) => console.log('Require confirmation:', e.target.checked)}
                                />
                            }
                            label="Require confirmation before execution"
                        />
                        
                        <TextField
                            label="Execution Delay (seconds)"
                            type="number"
                            defaultValue="0"
                            helperText="Delay execution by specified seconds"
                            fullWidth
                        />
                        
                        <TextField
                            label="Retry Attempts"
                            type="number"
                            defaultValue="3"
                            helperText="Number of retry attempts on failure"
                            fullWidth
                        />
                        
                        <TextField
                            label="Timeout (seconds)"
                            type="number"
                            defaultValue="30"
                            helperText="Maximum execution time"
                            fullWidth
                        />
                        
                        <Alert severity="info">
                            Configuration changes will be applied to this specific action instance.
                            To create reusable templates, use the Rules Manager.
                        </Alert>
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowConfig(false)}>Cancel</Button>
                    <Button 
                        variant="contained" 
                        onClick={() => {
                            onConfigure?.(config);
                            setShowConfig(false);
                        }}
                    >
                        Save Configuration
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default ActionPreview;