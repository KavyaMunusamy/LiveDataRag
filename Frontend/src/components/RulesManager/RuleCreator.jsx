import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    TextField,
    Button,
    Grid,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Chip,
    IconButton,
    Tooltip,
    Alert,
    Divider,
    Stack,
    Card,
    CardContent,
    CardHeader,
    Slider,
    Switch,
    FormControlLabel,
    Tabs,
    Tab,
    Autocomplete,
    InputAdornment,
    RadioGroup,
    Radio,
    FormLabel
} from '@mui/material';
import {
    Add,
    Remove,
    Save,
    PlayArrow,
    Code,
    Timeline,
    TrendingUp,
    Security,
    DataArray,
    SmartToy,
    AutoFixHigh,
    Psychology,
    Help,
    ContentCopy,
    History,
    CheckCircle,
    Error
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const RuleCreator = ({ onSave, onTest, initialRule = null, templates = [] }) => {
    const [activeTab, setActiveTab] = useState(0);
    const [rule, setRule] = useState(initialRule || {
        name: '',
        description: '',
        enabled: true,
        condition: {
            type: 'keyword',
            keywords: [],
            field: '',
            operator: 'greater_than',
            threshold: 0,
            pattern: ''
        },
        action: {
            type: 'alert',
            parameters: {},
            delay: 0,
            retry_attempts: 3
        },
        schedule: {
            enabled: false,
            cron_expression: '* * * * *'
        },
        notifications: {
            on_success: true,
            on_failure: true,
            channels: ['email', 'slack']
        }
    });

    const [keywords, setKeywords] = useState('');
    const [validationErrors, setValidationErrors] = useState({});

    const conditionTypes = [
        { value: 'keyword', label: 'Keyword Match', icon: <Code />, description: 'Match text against keywords' },
        { value: 'threshold', label: 'Threshold', icon: <Timeline />, description: 'Compare numeric values' },
        { value: 'pattern', label: 'Pattern Match', icon: <AutoFixHigh />, description: 'Regular expression pattern' },
        { value: 'composite', label: 'Composite Condition', icon: <Psychology />, description: 'Multiple conditions' }
    ];

    const actionTypes = [
        { value: 'alert', label: 'Send Alert', color: 'warning' },
        { value: 'api_call', label: 'API Call', color: 'primary' },
        { value: 'data_update', label: 'Update Data', color: 'success' },
        { value: 'workflow_trigger', label: 'Trigger Workflow', color: 'info' }
    ];

    const operators = [
        { value: 'greater_than', label: 'Greater Than' },
        { value: 'less_than', label: 'Less Than' },
        { value: 'equals', label: 'Equals' },
        { value: 'not_equals', label: 'Not Equals' },
        { value: 'between', label: 'Between' }
    ];

    const fields = [
        { value: 'price', label: 'Stock Price' },
        { value: 'volume', label: 'Trading Volume' },
        { value: 'sentiment', label: 'News Sentiment' },
        { value: 'temperature', label: 'Temperature' },
        { value: 'cpu_usage', label: 'CPU Usage' },
        { value: 'error_rate', label: 'Error Rate' }
    ];

    const handleConditionChange = (field, value) => {
        setRule(prev => ({
            ...prev,
            condition: {
                ...prev.condition,
                [field]: value
            }
        }));
        // Clear validation errors for this field
        setValidationErrors(prev => ({ ...prev, [field]: null }));
    };

    const handleActionChange = (field, value) => {
        setRule(prev => ({
            ...prev,
            action: {
                ...prev.action,
                [field]: value
            }
        }));
    };

    const handleKeywordsChange = (e) => {
        const value = e.target.value;
        setKeywords(value);
        const keywordArray = value.split(',').map(k => k.trim()).filter(k => k);
        handleConditionChange('keywords', keywordArray);
    };

    const validateRule = () => {
        const errors = {};
        
        if (!rule.name.trim()) {
            errors.name = 'Rule name is required';
        }
        
        if (rule.condition.type === 'keyword' && rule.condition.keywords.length === 0) {
            errors.keywords = 'At least one keyword is required';
        }
        
        if (rule.condition.type === 'threshold') {
            if (!rule.condition.field) {
                errors.field = 'Field is required for threshold condition';
            }
            if (rule.condition.threshold === null || rule.condition.threshold === '') {
                errors.threshold = 'Threshold value is required';
            }
        }
        
        if (rule.condition.type === 'pattern' && !rule.condition.pattern.trim()) {
            errors.pattern = 'Pattern is required';
        }
        
        setValidationErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSave = () => {
        if (validateRule()) {
            onSave?.(rule);
        }
    };

    const handleTest = () => {
        if (validateRule()) {
            onTest?.(rule);
        }
    };

    const loadTemplate = (template) => {
        setRule(template);
        setKeywords(template.condition.keywords?.join(', ') || '');
    };

    const renderConditionFields = () => {
        switch (rule.condition.type) {
            case 'keyword':
                return (
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <TextField
                                label="Keywords (comma-separated)"
                                value={keywords}
                                onChange={handleKeywordsChange}
                                error={!!validationErrors.keywords}
                                helperText={validationErrors.keywords || 'e.g., TSLA, stock, earnings'}
                                fullWidth
                                multiline
                                rows={2}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {rule.condition.keywords?.map((keyword, index) => (
                                    <Chip
                                        key={index}
                                        label={keyword}
                                        onDelete={() => {
                                            const newKeywords = [...rule.condition.keywords];
                                            newKeywords.splice(index, 1);
                                            handleConditionChange('keywords', newKeywords);
                                            setKeywords(newKeywords.join(', '));
                                        }}
                                    />
                                ))}
                            </Box>
                        </Grid>
                    </Grid>
                );

            case 'threshold':
                return (
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={4}>
                            <FormControl fullWidth error={!!validationErrors.field}>
                                <InputLabel>Field</InputLabel>
                                <Select
                                    value={rule.condition.field}
                                    label="Field"
                                    onChange={(e) => handleConditionChange('field', e.target.value)}
                                >
                                    {fields.map(field => (
                                        <MenuItem key={field.value} value={field.value}>
                                            {field.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <FormControl fullWidth>
                                <InputLabel>Operator</InputLabel>
                                <Select
                                    value={rule.condition.operator}
                                    label="Operator"
                                    onChange={(e) => handleConditionChange('operator', e.target.value)}
                                >
                                    {operators.map(op => (
                                        <MenuItem key={op.value} value={op.value}>
                                            {op.label}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <TextField
                                label="Threshold Value"
                                type="number"
                                value={rule.condition.threshold}
                                onChange={(e) => handleConditionChange('threshold', parseFloat(e.target.value))}
                                error={!!validationErrors.threshold}
                                helperText={validationErrors.threshold}
                                fullWidth
                                InputProps={{
                                    endAdornment: rule.condition.field === 'price' ? (
                                        <InputAdornment position="end">$</InputAdornment>
                                    ) : null
                                }}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <Alert severity="info">
                                This rule will trigger when {rule.condition.field} {rule.condition.operator.replace('_', ' ')} {rule.condition.threshold}
                            </Alert>
                        </Grid>
                    </Grid>
                );

            case 'pattern':
                return (
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <TextField
                                label="Regular Expression Pattern"
                                value={rule.condition.pattern}
                                onChange={(e) => handleConditionChange('pattern', e.target.value)}
                                error={!!validationErrors.pattern}
                                helperText={validationErrors.pattern || 'Use regex pattern for matching'}
                                fullWidth
                                placeholder="e.g., ^[A-Z]{1,5}$"
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <Alert severity="warning">
                                Regular expressions must be valid JavaScript regex patterns
                            </Alert>
                        </Grid>
                    </Grid>
                );

            default:
                return null;
        }
    };

    return (
        <Box>
            <Paper sx={{ p: 3, mb: 3 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h5" fontWeight="medium">
                        Create New Rule
                    </Typography>
                    <Stack direction="row" spacing={1}>
                        <Button
                            variant="outlined"
                            startIcon={<PlayArrow />}
                            onClick={handleTest}
                        >
                            Test Rule
                        </Button>
                        <Button
                            variant="contained"
                            startIcon={<Save />}
                            onClick={handleSave}
                        >
                            Save Rule
                        </Button>
                    </Stack>
                </Box>

                {/* Tabs */}
                <Tabs 
                    value={activeTab} 
                    onChange={(e, newValue) => setActiveTab(newValue)}
                    sx={{ mb: 3 }}
                >
                    <Tab label="Basic Info" />
                    <Tab label="Conditions" />
                    <Tab label="Actions" />
                    <Tab label="Schedule" />
                    <Tab label="Notifications" />
                </Tabs>

                {/* Tab Content */}
                {activeTab === 0 && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}>
                                <TextField
                                    label="Rule Name"
                                    value={rule.name}
                                    onChange={(e) => setRule(prev => ({ ...prev, name: e.target.value }))}
                                    error={!!validationErrors.name}
                                    helperText={validationErrors.name || 'Give your rule a descriptive name'}
                                    fullWidth
                                    required
                                />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={rule.enabled}
                                            onChange={(e) => setRule(prev => ({ ...prev, enabled: e.target.checked }))}
                                        />
                                    }
                                    label="Rule Enabled"
                                    sx={{ mt: 2 }}
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    label="Description"
                                    value={rule.description}
                                    onChange={(e) => setRule(prev => ({ ...prev, description: e.target.value }))}
                                    multiline
                                    rows={3}
                                    fullWidth
                                    helperText="Describe what this rule does and when it should trigger"
                                />
                            </Grid>
                            {templates.length > 0 && (
                                <Grid item xs={12}>
                                    <Typography variant="subtitle2" gutterBottom>
                                        Load from Template
                                    </Typography>
                                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                                        {templates.map((template, index) => (
                                            <Chip
                                                key={index}
                                                label={template.name}
                                                onClick={() => loadTemplate(template)}
                                                icon={<ContentCopy />}
                                                variant="outlined"
                                            />
                                        ))}
                                    </Stack>
                                </Grid>
                            )}
                        </Grid>
                    </motion.div>
                )}

                {activeTab === 1 && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}>
                                <FormControl fullWidth>
                                    <InputLabel>Condition Type</InputLabel>
                                    <Select
                                        value={rule.condition.type}
                                        label="Condition Type"
                                        onChange={(e) => handleConditionChange('type', e.target.value)}
                                    >
                                        {conditionTypes.map(type => (
                                            <MenuItem key={type.value} value={type.value}>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    {type.icon}
                                                    {type.label}
                                                </Box>
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12}>
                                <Card variant="outlined">
                                    <CardHeader
                                        title={
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                {conditionTypes.find(t => t.value === rule.condition.type)?.icon}
                                                <Typography>
                                                    {conditionTypes.find(t => t.value === rule.condition.type)?.label}
                                                </Typography>
                                            </Box>
                                        }
                                        subheader={conditionTypes.find(t => t.value === rule.condition.type)?.description}
                                    />
                                    <CardContent>
                                        {renderConditionFields()}
                                    </CardContent>
                                </Card>
                            </Grid>
                            <Grid item xs={12}>
                                <Alert severity="info">
                                    <Typography variant="subtitle2" gutterBottom>
                                        Rule Logic
                                    </Typography>
                                    The rule will trigger when the specified condition is met. Conditions are evaluated against real-time data streams.
                                </Alert>
                            </Grid>
                        </Grid>
                    </motion.div>
                )}

                {activeTab === 2 && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <Grid container spacing={3}>
                            <Grid item xs={12} md={6}>
                                <FormControl fullWidth>
                                    <InputLabel>Action Type</InputLabel>
                                    <Select
                                        value={rule.action.type}
                                        label="Action Type"
                                        onChange={(e) => handleActionChange('type', e.target.value)}
                                    >
                                        {actionTypes.map(action => (
                                            <MenuItem key={action.value} value={action.value}>
                                                <Chip
                                                    label={action.label}
                                                    color={action.color}
                                                    size="small"
                                                    sx={{ color: 'white' }}
                                                />
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} md={3}>
                                <TextField
                                    label="Delay (seconds)"
                                    type="number"
                                    value={rule.action.delay}
                                    onChange={(e) => handleActionChange('delay', parseInt(e.target.value))}
                                    fullWidth
                                    helperText="Delay before executing action"
                                />
                            </Grid>
                            <Grid item xs={12} md={3}>
                                <TextField
                                    label="Retry Attempts"
                                    type="number"
                                    value={rule.action.retry_attempts}
                                    onChange={(e) => handleActionChange('retry_attempts', parseInt(e.target.value))}
                                    fullWidth
                                    helperText="Retry on failure"
                                />
                            </Grid>
                            
                            {/* Action-specific parameters */}
                            <Grid item xs={12}>
                                <Card variant="outlined">
                                    <CardHeader
                                        title="Action Parameters"
                                        subheader="Configure parameters specific to this action type"
                                    />
                                    <CardContent>
                                        {rule.action.type === 'alert' && (
                                            <Grid container spacing={2}>
                                                <Grid item xs={12}>
                                                    <TextField
                                                        label="Alert Message"
                                                        multiline
                                                        rows={3}
                                                        fullWidth
                                                        placeholder="Enter the alert message to send..."
                                                    />
                                                </Grid>
                                                <Grid item xs={12} md={6}>
                                                    <FormControl fullWidth>
                                                        <FormLabel>Alert Channels</FormLabel>
                                                        <RadioGroup row defaultValue="all">
                                                            <FormControlLabel value="email" control={<Radio />} label="Email" />
                                                            <FormControlLabel value="slack" control={<Radio />} label="Slack" />
                                                            <FormControlLabel value="sms" control={<Radio />} label="SMS" />
                                                        </RadioGroup>
                                                    </FormControl>
                                                </Grid>
                                                <Grid item xs={12} md={6}>
                                                    <FormControl fullWidth>
                                                        <InputLabel>Priority</InputLabel>
                                                        <Select defaultValue="medium">
                                                            <MenuItem value="low">Low</MenuItem>
                                                            <MenuItem value="medium">Medium</MenuItem>
                                                            <MenuItem value="high">High</MenuItem>
                                                            <MenuItem value="critical">Critical</MenuItem>
                                                        </Select>
                                                    </FormControl>
                                                </Grid>
                                            </Grid>
                                        )}

                                        {rule.action.type === 'api_call' && (
                                            <Grid container spacing={2}>
                                                <Grid item xs={12} md={6}>
                                                    <TextField
                                                        label="API Endpoint"
                                                        fullWidth
                                                        placeholder="https://api.example.com/endpoint"
                                                    />
                                                </Grid>
                                                <Grid item xs={12} md={6}>
                                                    <FormControl fullWidth>
                                                        <InputLabel>HTTP Method</InputLabel>
                                                        <Select defaultValue="POST">
                                                            <MenuItem value="GET">GET</MenuItem>
                                                            <MenuItem value="POST">POST</MenuItem>
                                                            <MenuItem value="PUT">PUT</MenuItem>
                                                            <MenuItem value="DELETE">DELETE</MenuItem>
                                                        </Select>
                                                    </FormControl>
                                                </Grid>
                                                <Grid item xs={12}>
                                                    <TextField
                                                        label="Request Body (JSON)"
                                                        multiline
                                                        rows={4}
                                                        fullWidth
                                                        placeholder='{"key": "value"}'
                                                    />
                                                </Grid>
                                            </Grid>
                                        )}
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </motion.div>
                )}

                {activeTab === 3 && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={rule.schedule.enabled}
                                            onChange={(e) => setRule(prev => ({
                                                ...prev,
                                                schedule: { ...prev.schedule, enabled: e.target.checked }
                                            }))}
                                        />
                                    }
                                    label="Enable Scheduled Execution"
                                />
                            </Grid>
                            
                            {rule.schedule.enabled && (
                                <>
                                    <Grid item xs={12} md={6}>
                                        <TextField
                                            label="Cron Expression"
                                            value={rule.schedule.cron_expression}
                                            onChange={(e) => setRule(prev => ({
                                                ...prev,
                                                schedule: { ...prev.schedule, cron_expression: e.target.value }
                                            }))}
                                            fullWidth
                                            helperText="e.g., */5 * * * * for every 5 minutes"
                                        />
                                    </Grid>
                                    <Grid item xs={12} md={6}>
                                        <Alert severity="info">
                                            <Typography variant="subtitle2">Cron Expression Help</Typography>
                                            • Minute (0-59) • Hour (0-23) • Day of month (1-31)<br/>
                                            • Month (1-12) • Day of week (0-6, 0=Sunday)
                                        </Alert>
                                    </Grid>
                                </>
                            )}
                        </Grid>
                    </motion.div>
                )}

                {activeTab === 4 && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={rule.notifications.on_success}
                                            onChange={(e) => setRule(prev => ({
                                                ...prev,
                                                notifications: { ...prev.notifications, on_success: e.target.checked }
                                            }))}
                                        />
                                    }
                                    label="Notify on Successful Execution"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={rule.notifications.on_failure}
                                            onChange={(e) => setRule(prev => ({
                                                ...prev,
                                                notifications: { ...prev.notifications, on_failure: e.target.checked }
                                            }))}
                                        />
                                    }
                                    label="Notify on Failed Execution"
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <FormControl fullWidth>
                                    <InputLabel>Notification Channels</InputLabel>
                                    <Select
                                        multiple
                                        value={rule.notifications.channels}
                                        onChange={(e) => setRule(prev => ({
                                            ...prev,
                                            notifications: { ...prev.notifications, channels: e.target.value }
                                        }))}
                                        renderValue={(selected) => (
                                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                                {selected.map(value => (
                                                    <Chip key={value} label={value} size="small" />
                                                ))}
                                            </Box>
                                        )}
                                    >
                                        {['email', 'slack', 'sms', 'webhook', 'push'].map(channel => (
                                            <MenuItem key={channel} value={channel}>
                                                {channel.charAt(0).toUpperCase() + channel.slice(1)}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                        </Grid>
                    </motion.div>
                )}
            </Paper>

            {/* Quick Actions */}
            <Paper sx={{ p: 2 }}>
                <Stack direction="row" spacing={2} justifyContent="center">
                    <Button
                        variant="outlined"
                        startIcon={<History />}
                        onClick={() => console.log('View history')}
                    >
                        View History
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<SmartToy />}
                        onClick={() => console.log('AI suggestions')}
                    >
                        AI Suggestions
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<Help />}
                        onClick={() => console.log('Help')}
                    >
                        Help & Examples
                    </Button>
                </Stack>
            </Paper>
        </Box>
    );
};

export default RuleCreator;