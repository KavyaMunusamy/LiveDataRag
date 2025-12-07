import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    Chip,
    Tooltip,
    Divider,
    Alert,
    AlertTitle,
    Collapse,
    Button,
    Stack,
    LinearProgress,
    Card,
    CardContent,
    CardHeader,
    CardActions,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Badge
} from '@mui/material';
import {
    ExpandMore,
    ExpandLess,
    ContentCopy,
    ThumbUp,
    ThumbDown,
    Refresh,
    Download,
    Share,
    Timeline,
    DataArray,
    CheckCircle,
    Warning,
    Error,
    Info,
    AutoGraph,
    Psychology,
    Security,
    HistoryToggleOff,
    Science,
    BarChart,
    TableChart,
    TextSnippet,
    Code,
    Link
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { motion, AnimatePresence } from 'framer-motion';
import { format, parseISO } from 'date-fns';
import './QueryInterface.css';

const ResultsDisplay = ({ 
    results = null, 
    isLoading = false,
    onRegenerate,
    onFeedback,
    query = ''
}) => {
    const [expandedSections, setExpandedSections] = useState({});
    const [copied, setCopied] = useState(false);

    if (!results && !isLoading) {
        return (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                    No results to display
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Enter a query to analyze real-time data
                </Typography>
            </Paper>
        );
    }

    if (isLoading) {
        return (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                    Analyzing Query...
                </Typography>
                <LinearProgress sx={{ my: 2 }} />
                <Typography variant="body2" color="text.secondary">
                    Retrieving real-time data and generating insights
                </Typography>
            </Paper>
        );
    }

    const {
        response,
        retrieval_metadata,
        decision,
        action_result,
        timestamp
    } = results;

    const toggleSection = (section) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const formatDataForDisplay = (data) => {
        if (typeof data === 'string') return data;
        if (Array.isArray(data)) {
            return data.map((item, idx) => (
                <Typography key={idx} variant="body2" sx={{ mb: 1 }}>
                    • {item}
                </Typography>
            ));
        }
        return JSON.stringify(data, null, 2);
    };

    const getDecisionColor = (decision) => {
        if (!decision) return 'default';
        if (decision.action_required) {
            if (decision.confidence > 0.8) return 'success';
            if (decision.confidence > 0.5) return 'warning';
            return 'error';
        }
        return 'info';
    };

    const getActionStatusColor = (status) => {
        switch (status) {
            case 'executed': return 'success';
            case 'failed': return 'error';
            case 'pending': return 'warning';
            case 'requires_confirmation': return 'info';
            default: return 'default';
        }
    };

    return (
        <Box>
            {/* Header */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                        <Typography variant="h6" gutterBottom>
                            Analysis Results
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                            Query: "{query}"
                        </Typography>
                    </Box>
                    <Stack direction="row" spacing={1}>
                        <Tooltip title="Copy results">
                            <IconButton 
                                size="small" 
                                onClick={() => copyToClipboard(JSON.stringify(results, null, 2))}
                                color={copied ? 'success' : 'default'}
                            >
                                <ContentCopy />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Regenerate response">
                            <IconButton size="small" onClick={onRegenerate}>
                                <Refresh />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Download as JSON">
                            <IconButton size="small" onClick={() => console.log('Download')}>
                                <Download />
                            </IconButton>
                        </Tooltip>
                    </Stack>
                </Box>
                <LinearProgress 
                    variant="determinate" 
                    value={100} 
                    sx={{ mt: 1, height: 2 }}
                />
            </Paper>

            {/* Main Response */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <Paper sx={{ p: 3, mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                        <Psychology sx={{ color: 'primary.main', mt: 0.5 }} />
                        <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="h6" gutterBottom>
                                AI Analysis
                            </Typography>
                            <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                                {response}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                Generated: {format(parseISO(timestamp), 'PPpp')}
                            </Typography>
                        </Box>
                    </Box>
                </Paper>
            </motion.div>

            {/* Action Decision Section */}
            {decision && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                >
                    <Paper sx={{ p: 3, mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <AutoGraph sx={{ color: getDecisionColor(decision) }} />
                                <Typography variant="h6">
                                    Action Decision
                                </Typography>
                            </Box>
                            <Chip
                                icon={decision.action_required ? <CheckCircle /> : <Info />}
                                label={decision.action_required ? 'ACTION REQUIRED' : 'MONITORING ONLY'}
                                color={getDecisionColor(decision)}
                                variant="filled"
                            />
                        </Box>

                        <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                            Decision Details
                                        </Typography>
                                        <List dense>
                                            <ListItem>
                                                <ListItemIcon>
                                                    <Psychology />
                                                </ListItemIcon>
                                                <ListItemText 
                                                    primary="Decision Source" 
                                                    secondary={decision.decision_source || 'AI Analysis'}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemIcon>
                                                    <Security />
                                                </ListItemIcon>
                                                <ListItemText 
                                                    primary="Confidence" 
                                                    secondary={`${(decision.confidence * 100).toFixed(1)}%`}
                                                />
                                            </ListItem>
                                            <ListItem>
                                                <ListItemIcon>
                                                    <Timeline />
                                                </ListItemIcon>
                                                <ListItemText 
                                                    primary="Urgency" 
                                                    secondary={`${decision.urgency_score || 'N/A'}/10`}
                                                />
                                            </ListItem>
                                        </List>
                                    </CardContent>
                                </Card>
                            </Grid>
                            
                            <Grid item xs={12} md={6}>
                                <Card variant="outlined">
                                    <CardContent>
                                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                            Reasoning
                                        </Typography>
                                        <Typography variant="body2">
                                            {decision.reason || 'No reasoning provided'}
                                        </Typography>
                                        {decision.matching_rule && (
                                            <Alert severity="info" sx={{ mt: 2 }}>
                                                Matched rule: {decision.matching_rule}
                                            </Alert>
                                        )}
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </Paper>
                </motion.div>
            )}

            {/* Action Result */}
            {action_result && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                >
                    <Paper sx={{ p: 3, mb: 2 }}>
                        <Accordion 
                            expanded={expandedSections.actionResult || false}
                            onChange={() => toggleSection('actionResult')}
                        >
                            <AccordionSummary expandIcon={<ExpandMore />}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                                    <Badge 
                                        color={getActionStatusColor(action_result.status)} 
                                        variant="dot"
                                    >
                                        <Science />
                                    </Badge>
                                    <Box sx={{ flexGrow: 1 }}>
                                        <Typography variant="h6">
                                            Action Execution
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Status: {action_result.status.toUpperCase()}
                                        </Typography>
                                    </Box>
                                    <Chip
                                        label={action_result.action_type || 'Unknown'}
                                        color={getActionStatusColor(action_result.status)}
                                        size="small"
                                    />
                                </Box>
                            </AccordionSummary>
                            <AccordionDetails>
                                <TableContainer>
                                    <Table size="small">
                                        <TableBody>
                                            <TableRow>
                                                <TableCell><strong>Action ID</strong></TableCell>
                                                <TableCell>{action_result.action_id}</TableCell>
                                            </TableRow>
                                            <TableRow>
                                                <TableCell><strong>Timestamp</strong></TableCell>
                                                <TableCell>
                                                    {format(parseISO(action_result.timestamp), 'PPpp')}
                                                </TableCell>
                                            </TableRow>
                                            {action_result.reason && (
                                                <TableRow>
                                                    <TableCell><strong>Reason</strong></TableCell>
                                                    <TableCell>{action_result.reason}</TableCell>
                                                </TableRow>
                                            )}
                                            {action_result.error && (
                                                <TableRow>
                                                    <TableCell><strong>Error</strong></TableCell>
                                                    <TableCell>
                                                        <Alert severity="error">
                                                            {action_result.error}
                                                        </Alert>
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                            {action_result.result && (
                                                <TableRow>
                                                    <TableCell><strong>Result</strong></TableCell>
                                                    <TableCell>
                                                        <Paper 
                                                            variant="outlined" 
                                                            sx={{ p: 1, bgcolor: 'success.light', color: 'success.contrastText' }}
                                                        >
                                                            {typeof action_result.result === 'string' 
                                                                ? action_result.result 
                                                                : JSON.stringify(action_result.result, null, 2)}
                                                        </Paper>
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </AccordionDetails>
                        </Accordion>
                    </Paper>
                </motion.div>
            )}

            {/* Retrieval Metadata */}
            {retrieval_metadata && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                >
                    <Paper sx={{ p: 3 }}>
                        <Accordion 
                            expanded={expandedSections.metadata || false}
                            onChange={() => toggleSection('metadata')}
                        >
                            <AccordionSummary expandIcon={<ExpandMore />}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                    <DataArray />
                                    <Typography variant="h6">
                                        Data Retrieval Details
                                    </Typography>
                                </Box>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Grid container spacing={2}>
                                    <Grid item xs={12} md={6}>
                                        <Card variant="outlined">
                                            <CardHeader 
                                                title="Source Information"
                                                avatar={<BarChart />}
                                            />
                                            <CardContent>
                                                <List dense>
                                                    <ListItem>
                                                        <ListItemText 
                                                            primary="Data Sources" 
                                                            secondary={retrieval_metadata.context_type || 'Multiple'}
                                                        />
                                                    </ListItem>
                                                    <ListItem>
                                                        <ListItemText 
                                                            primary="Time Range" 
                                                            secondary={retrieval_metadata.time_range_used || 'N/A'}
                                                        />
                                                    </ListItem>
                                                    <ListItem>
                                                        <ListItemText 
                                                            primary="Data Points" 
                                                            secondary={retrieval_metadata.result_count || 0}
                                                        />
                                                    </ListItem>
                                                </List>
                                            </CardContent>
                                        </Card>
                                    </Grid>
                                    
                                    <Grid item xs={12} md={6}>
                                        <Card variant="outlined">
                                            <CardHeader 
                                                title="Data Freshness"
                                                avatar={<HistoryToggleOff />}
                                            />
                                            <CardContent>
                                                <List dense>
                                                    <ListItem>
                                                        <ListItemText 
                                                            primary="Freshness Score" 
                                                            secondary={`${(retrieval_metadata.freshness_score * 100 || 0).toFixed(1)}%`}
                                                        />
                                                    </ListItem>
                                                    <ListItem>
                                                        <ListItemText 
                                                            primary="Newest Data" 
                                                            secondary={retrieval_metadata.newest_data 
                                                                ? format(parseISO(retrieval_metadata.newest_data), 'PPpp')
                                                                : 'N/A'
                                                            }
                                                        />
                                                    </ListItem>
                                                    <ListItem>
                                                        <ListItemText 
                                                            primary="Oldest Data" 
                                                            secondary={retrieval_metadata.oldest_data 
                                                                ? format(parseISO(retrieval_metadata.oldest_data), 'PPpp')
                                                                : 'N/A'
                                                            }
                                                        />
                                                    </ListItem>
                                                </List>
                                            </CardContent>
                                        </Card>
                                    </Grid>
                                </Grid>
                                
                                {retrieval_metadata.raw_results && (
                                    <Box sx={{ mt: 3 }}>
                                        <Typography variant="subtitle2" gutterBottom>
                                            Raw Data Preview
                                        </Typography>
                                        <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto' }}>
                                            <SyntaxHighlighter 
                                                language="json" 
                                                style={vscDarkPlus}
                                                customStyle={{ margin: 0, fontSize: '0.875rem' }}
                                            >
                                                {JSON.stringify(retrieval_metadata.raw_results.slice(0, 3), null, 2)}
                                            </SyntaxHighlighter>
                                        </Paper>
                                    </Box>
                                )}
                            </AccordionDetails>
                        </Accordion>
                    </Paper>
                </motion.div>
            )}

            {/* Feedback Section */}
            <Paper sx={{ p: 2, mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                        Was this analysis helpful?
                    </Typography>
                    <Stack direction="row" spacing={1}>
                        <Button
                            size="small"
                            startIcon={<ThumbUp />}
                            onClick={() => onFeedback?.('positive')}
                            variant="outlined"
                        >
                            Helpful
                        </Button>
                        <Button
                            size="small"
                            startIcon={<ThumbDown />}
                            onClick={() => onFeedback?.('negative')}
                            variant="outlined"
                            color="error"
                        >
                            Not Helpful
                        </Button>
                        <Button
                            size="small"
                            startIcon={<Share />}
                            onClick={() => console.log('Share results')}
                            variant="outlined"
                        >
                            Share
                        </Button>
                    </Stack>
                </Box>
            </Paper>
        </Box>
    );
};

export default ResultsDisplay;