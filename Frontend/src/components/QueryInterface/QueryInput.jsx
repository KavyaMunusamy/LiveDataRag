import React, { useState, useRef, useEffect } from 'react';
import {
    Box,
    Paper,
    TextField,
    IconButton,
    Button,
    Chip,
    Tooltip,
    Menu,
    MenuItem,
    Divider,
    Typography,
    InputAdornment,
    Autocomplete,
    FormControl,
    InputLabel,
    Select,
    Stack,
    Slider,
    Switch,
    FormControlLabel,
    Alert,
    Collapse,
    CircularProgress
} from '@mui/material';
import {
    Send,
    Mic,
    AttachFile,
    History,
    TrendingUp,
    Timeline,
    DataArray,
    Security,
    Code,
    MoreVert,
    Clear,
    Save,
    SmartToy,
    AutoFixHigh,
    Psychology,
    Search,
    FilterAlt,
    Timer
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import './QueryInterface.css';

const QueryInput = ({ 
    onSubmit, 
    onFileUpload, 
    isLoading = false,
    recentQueries = [],
    suggestions = []
}) => {
    const [query, setQuery] = useState('');
    const [contextType, setContextType] = useState('auto');
    const [timeRange, setTimeRange] = useState('6h');
    const [advancedOpen, setAdvancedOpen] = useState(false);
    const [anchorEl, setAnchorEl] = useState(null);
    const [safetyLevel, setSafetyLevel] = useState('medium');
    const [actionThreshold, setActionThreshold] = useState(75);
    const [includeHistory, setIncludeHistory] = useState(true);
    const [selectedSuggestion, setSelectedSuggestion] = useState(null);
    const textareaRef = useRef(null);

    const contextTypes = [
        { value: 'auto', label: 'Auto-detect', icon: <Psychology /> },
        { value: 'financial', label: 'Financial Data', icon: <TrendingUp /> },
        { value: 'news', label: 'News & Media', icon: <Timeline /> },
        { value: 'technical', label: 'Technical Analysis', icon: <Code /> },
        { value: 'security', label: 'Security & Monitoring', icon: <Security /> },
        { value: 'all', label: 'All Sources', icon: <DataArray /> }
    ];

    const timeRanges = [
        { value: '1h', label: 'Last Hour' },
        { value: '6h', label: 'Last 6 Hours' },
        { value: '24h', label: 'Last 24 Hours' },
        { value: '7d', label: 'Last Week' },
        { value: '30d', label: 'Last Month' }
    ];

    const safetyLevels = [
        { value: 'low', label: 'Low (Maximum Automation)', description: 'Allow most autonomous actions' },
        { value: 'medium', label: 'Medium (Balanced)', description: 'Require confirmation for critical actions' },
        { value: 'high', label: 'High (Conservative)', description: 'Manual confirmation for all actions' }
    ];

    const exampleQueries = [
        "Monitor TSLA stock and alert me if it drops 5% on high volume",
        "What are the latest developments in AI chip companies?",
        "Check for any security vulnerabilities in the past 24 hours",
        "Analyze social media sentiment about our product launch",
        "Compare NVIDIA and AMD stock performance this week"
    ];

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    }, [query]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim() && !isLoading) {
            const queryData = {
                query: query.trim(),
                context_type: contextType,
                time_range: timeRange,
                safety_level: safetyLevel,
                action_threshold: actionThreshold,
                include_history: includeHistory
            };
            onSubmit(queryData);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleSubmit(e);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setQuery(suggestion);
        setSelectedSuggestion(suggestion);
    };

    const handleFileUpload = (e) => {
        const file = e.target.files[0];
        if (file && onFileUpload) {
            onFileUpload(file);
        }
    };

    const handleClear = () => {
        setQuery('');
        setSelectedSuggestion(null);
    };

    const handleSaveQuery = () => {
        // Save query to favorites
        console.log('Saving query:', query);
        setAnchorEl(null);
    };

    return (
        <Paper 
            elevation={3} 
            sx={{ 
                p: 3, 
                borderRadius: 2,
                background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
            }}
        >
            <form onSubmit={handleSubmit}>
                {/* Query Input Area */}
                <Box sx={{ position: 'relative' }}>
                    <TextField
                        inputRef={textareaRef}
                        fullWidth
                        multiline
                        minRows={2}
                        maxRows={6}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask anything about real-time data... (Ctrl+Enter to send)"
                        variant="outlined"
                        disabled={isLoading}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start">
                                    <Search />
                                </InputAdornment>
                            ),
                            endAdornment: query && (
                                <InputAdornment position="end">
                                    <Tooltip title="Clear">
                                        <IconButton onClick={handleClear} size="small">
                                            <Clear />
                                        </IconButton>
                                    </Tooltip>
                                </InputAdornment>
                            )
                        }}
                        sx={{
                            '& .MuiOutlinedInput-root': {
                                fontSize: '1.1rem',
                                borderRadius: 2
                            }
                        }}
                    />

                    {/* Character Counter */}
                    <Typography 
                        variant="caption" 
                        color="text.secondary"
                        sx={{ position: 'absolute', right: 8, bottom: 8 }}
                    >
                        {query.length}/1000
                    </Typography>
                </Box>

                {/* Quick Actions Bar */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, mb: 1 }}>
                    <Stack direction="row" spacing={1}>
                        <Tooltip title="Voice input (coming soon)">
                            <IconButton size="small" disabled>
                                <Mic />
                            </IconButton>
                        </Tooltip>
                        
                        <Tooltip title="Attach file for context">
                            <IconButton 
                                size="small" 
                                component="label"
                                disabled={isLoading}
                            >
                                <AttachFile />
                                <input
                                    type="file"
                                    hidden
                                    onChange={handleFileUpload}
                                    accept=".txt,.pdf,.csv,.json"
                                />
                            </IconButton>
                        </Tooltip>

                        <Tooltip title="Query history">
                            <IconButton size="small" onClick={() => console.log('Show history')}>
                                <History />
                            </IconButton>
                        </Tooltip>

                        <Tooltip title="More options">
                            <IconButton 
                                size="small" 
                                onClick={(e) => setAnchorEl(e.currentTarget)}
                            >
                                <MoreVert />
                            </IconButton>
                        </Tooltip>
                    </Stack>

                    <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        endIcon={isLoading ? <CircularProgress size={20} /> : <Send />}
                        disabled={!query.trim() || isLoading}
                        sx={{ borderRadius: 2 }}
                    >
                        {isLoading ? 'Analyzing...' : 'Analyze'}
                    </Button>
                </Box>

                {/* Options Menu */}
                <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={() => setAnchorEl(null)}
                >
                    <MenuItem onClick={handleSaveQuery}>
                        <Save sx={{ mr: 1 }} />
                        Save as Template
                    </MenuItem>
                    <MenuItem onClick={() => setAdvancedOpen(!advancedOpen)}>
                        <AutoFixHigh sx={{ mr: 1 }} />
                        Advanced Options
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={() => setAnchorEl(null)}>
                        <SmartToy sx={{ mr: 1 }} />
                        AI Suggestions
                    </MenuItem>
                </Menu>

                {/* Advanced Options */}
                <Collapse in={advancedOpen}>
                    <Paper variant="outlined" sx={{ p: 2, mt: 2, borderRadius: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                            Advanced Settings
                        </Typography>
                        
                        <Grid container spacing={2}>
                            <Grid item xs={12} sm={6}>
                                <FormControl fullWidth size="small">
                                    <InputLabel>Context Type</InputLabel>
                                    <Select
                                        value={contextType}
                                        label="Context Type"
                                        onChange={(e) => setContextType(e.target.value)}
                                    >
                                        {contextTypes.map((type) => (
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
                            
                            <Grid item xs={12} sm={6}>
                                <FormControl fullWidth size="small">
                                    <InputLabel>Time Range</InputLabel>
                                    <Select
                                        value={timeRange}
                                        label="Time Range"
                                        onChange={(e) => setTimeRange(e.target.value)}
                                    >
                                        {timeRanges.map((range) => (
                                            <MenuItem key={range.value} value={range.value}>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Timer fontSize="small" />
                                                    {range.label}
                                                </Box>
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                            
                            <Grid item xs={12}>
                                <Typography variant="body2" gutterBottom>
                                    Safety Level: {safetyLevels.find(s => s.value === safetyLevel)?.label}
                                </Typography>
                                <Slider
                                    value={safetyLevel === 'low' ? 0 : safetyLevel === 'medium' ? 50 : 100}
                                    step={50}
                                    marks={[
                                        { value: 0, label: 'Low' },
                                        { value: 50, label: 'Medium' },
                                        { value: 100, label: 'High' }
                                    ]}
                                    onChange={(e, value) => {
                                        const level = value === 0 ? 'low' : value === 50 ? 'medium' : 'high';
                                        setSafetyLevel(level);
                                    }}
                                    sx={{ mt: 1 }}
                                />
                                <Typography variant="caption" color="text.secondary">
                                    {safetyLevels.find(s => s.value === safetyLevel)?.description}
                                </Typography>
                            </Grid>
                            
                            <Grid item xs={12}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <Typography variant="body2">
                                        Action Confidence Threshold: {actionThreshold}%
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        Higher = More conservative
                                    </Typography>
                                </Box>
                                <Slider
                                    value={actionThreshold}
                                    onChange={(e, value) => setActionThreshold(value)}
                                    min={50}
                                    max={95}
                                    step={5}
                                    marks={[
                                        { value: 50, label: '50%' },
                                        { value: 75, label: '75%' },
                                        { value: 90, label: '90%' }
                                    ]}
                                />
                            </Grid>
                            
                            <Grid item xs={12}>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={includeHistory}
                                            onChange={(e) => setIncludeHistory(e.target.checked)}
                                            size="small"
                                        />
                                    }
                                    label="Include historical context in analysis"
                                />
                            </Grid>
                        </Grid>
                    </Paper>
                </Collapse>

                {/* Example Queries */}
                <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                        Try these examples:
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                        {exampleQueries.map((example, index) => (
                            <motion.div
                                key={index}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                            >
                                <Chip
                                    label={example}
                                    size="small"
                                    onClick={() => handleSuggestionClick(example)}
                                    sx={{ mb: 1 }}
                                    variant={selectedSuggestion === example ? "filled" : "outlined"}
                                    color={selectedSuggestion === example ? "primary" : "default"}
                                />
                            </motion.div>
                        ))}
                    </Stack>
                </Box>

                {/* Recent Queries */}
                {recentQueries.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                            Recent queries:
                        </Typography>
                        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                            {recentQueries.slice(0, 3).map((recent, index) => (
                                <Chip
                                    key={index}
                                    label={recent}
                                    size="small"
                                    onClick={() => handleSuggestionClick(recent)}
                                    onDelete={() => console.log('Delete:', recent)}
                                    deleteIcon={<Clear />}
                                    variant="outlined"
                                />
                            ))}
                        </Stack>
                    </Box>
                )}

                {/* AI Suggestions */}
                {suggestions.length > 0 && (
                    <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="caption">
                            AI Suggestions: {suggestions.join(', ')}
                        </Typography>
                    </Alert>
                )}
            </form>
        </Paper>
    );
};

export default QueryInput;