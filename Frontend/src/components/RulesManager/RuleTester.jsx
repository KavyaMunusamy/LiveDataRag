import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    TextField,
    Alert,
    AlertTitle,
    Stack,
    Divider,
    LinearProgress,
    Chip,
    Grid,
    Card,
    CardContent,
    CardHeader,
    IconButton,
    Tooltip,
    Collapse,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Accordion,
    AccordionSummary,
    AccordionDetails
} from '@mui/material';
import {
    PlayArrow,
    CheckCircle,
    Error,
    Warning,
    Info,
    ExpandMore,
    ContentCopy,
    Refresh,
    Timeline,
    AutoGraph,
    Psychology,
    Security,
    History
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { motion } from 'framer-motion';
import { format } from 'date-fns';

const RuleTester = ({ rule = null, onTest, testResults = null, isLoading = false }) => {
    const [testData, setTestData] = useState('');
    const [expanded, setExpanded] = useState(false);

    const defaultTestData = rule ? JSON.stringify({
        timestamp: new Date().toISOString(),
        data_type: 'financial_quote',
        symbol: 'TSLA',
        price: 195.42,
        change: -5.67,
        change_percent: '-2.83%',
        volume: 12500000
    }, null, 2) : '';

    const handleTest = () => {
        try {
            const parsedData = testData ? JSON.parse(testData) : JSON.parse(defaultTestData);
            onTest?.(rule, parsedData);
        } catch (error) {
            alert('Invalid JSON data: ' + error.message);
        }
    };

    const getTestStatus = () => {
        if (!testResults) return null;
        
        if (testResults.match) {
            return {
                color: 'success',
                icon: <CheckCircle />,
                title: 'Rule Matched',
                message: 'The test data would trigger this rule'
            };
        } else {
            return {
                color: 'info',
                icon: <Info />,
                title: 'No Match',
                message: 'The test data does not trigger this rule'
            };
        }
    };

    const renderConditionCheck = () => {
        if (!testResults?.condition_checks) return null;

        return (
            <Grid container spacing={2}>
                {testResults.condition_checks.map((check, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                        <Card variant="outlined">
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    {check.passed ? 
                                        <CheckCircle sx={{ color: 'success.main', mr: 1 }} /> :
                                        <Error sx={{ color: 'error.main', mr: 1 }} />
                                    }
                                    <Typography variant="subtitle2">
                                        {check.condition}
                                    </Typography>
                                </Box>
                                <Typography variant="body2" color="text.secondary">
                                    Expected: {check.expected}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Actual: {check.actual}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        );
    };

    const status = getTestStatus();

    return (
        <Box>
            <Paper sx={{ p: 3, mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h5" fontWeight="medium">
                        <AutoGraph sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Rule Tester
                    </Typography>
                    <Stack direction="row" spacing={1}>
                        <Tooltip title="Reset test">
                            <IconButton onClick={() => setTestData('')}>
                                <Refresh />
                            </IconButton>
                        </Tooltip>
                        <Button
                            variant="contained"
                            startIcon={<PlayArrow />}
                            onClick={handleTest}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Testing...' : 'Test Rule'}
                        </Button>
                    </Stack>
                </Box>

                {/* Rule Information */}
                {rule && (
                    <Alert 
                        severity="info" 
                        sx={{ mb: 3 }}
                        action={
                            <Button 
                                size="small" 
                                onClick={() => setExpanded(!expanded)}
                            >
                                {expanded ? 'Hide' : 'Show'} Details
                            </Button>
                        }
                    >
                        <AlertTitle>Testing Rule: {rule.name}</AlertTitle>
                        {rule.description}
                    </Alert>
                )}

                <Collapse in={expanded}>
                    <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                        <Typography variant="subtitle2" gutterBottom>
                            Rule Configuration
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                                <Typography variant="caption" color="text.secondary" display="block">
                                    Condition Type
                                </Typography>
                                <Typography variant="body2">
                                    {rule.condition?.type}
                                </Typography>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Typography variant="caption" color="text.secondary" display="block">
                                    Action Type
                                </Typography>
                                <Typography variant="body2">
                                    {rule.action?.type}
                                </Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <Typography variant="caption" color="text.secondary" display="block">
                                    Condition Details
                                </Typography>
                                <Paper 
                                    variant="outlined" 
                                    sx={{ 
                                        p: 1, 
                                        mt: 0.5,
                                        fontFamily: 'monospace',
                                        fontSize: '0.875rem',
                                        maxHeight: 150,
                                        overflow: 'auto'
                                    }}
                                >
                                    <pre style={{ margin: 0 }}>
                                        {JSON.stringify(rule.condition, null, 2)}
                                    </pre>
                                </Paper>
                            </Grid>
                        </Grid>
                    </Paper>
                </Collapse>

                {/* Test Data Input */}
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <Card variant="outlined" sx={{ height: '100%' }}>
                            <CardHeader
                                title="Test Data Input"
                                subheader="Provide JSON data to test against the rule"
                                action={
                                    <Tooltip title="Load example">
                                        <IconButton 
                                            size="small" 
                                            onClick={() => setTestData(defaultTestData)}
                                        >
                                            <ContentCopy />
                                        </IconButton>
                                    </Tooltip>
                                }
                            />
                            <CardContent>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={10}
                                    value={testData}
                                    onChange={(e) => setTestData(e.target.value)}
                                    placeholder="Enter JSON test data..."
                                    sx={{ fontFamily: 'monospace' }}
                                />
                                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                                    Provide JSON data that matches your data stream format
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <Card variant="outlined" sx={{ height: '100%' }}>
                            <CardHeader
                                title="Test Results"
                                subheader="See how the rule evaluates your test data"
                            />
                            <CardContent>
                                {isLoading ? (
                                    <Box sx={{ textAlign: 'center', py: 4 }}>
                                        <Typography variant="h6" gutterBottom>
                                            Testing Rule...
                                        </Typography>
                                        <LinearProgress sx={{ my: 2 }} />
                                        <Typography variant="caption" color="text.secondary">
                                            Evaluating conditions and checking for matches
                                        </Typography>
                                    </Box>
                                ) : testResults ? (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                    >
                                        <Alert 
                                            severity={status.color} 
                                            icon={status.icon}
                                            sx={{ mb: 3 }}
                                        >
                                            <AlertTitle>{status.title}</AlertTitle>
                                            {status.message}
                                        </Alert>

                                        {testResults.match && (
                                            <Alert severity="warning" sx={{ mb: 3 }}>
                                                <AlertTitle>Action Would Execute</AlertTitle>
                                                The following action would be triggered:
                                                <Typography variant="body2" sx={{ mt: 1 }}>
                                                    {JSON.stringify(testResults.proposed_action, null, 2)}
                                                </Typography>
                                            </Alert>
                                        )}

                                        {testResults.condition_checks && (
                                            <Accordion>
                                                <AccordionSummary expandIcon={<ExpandMore />}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <Psychology />
                                                        <Typography>Condition Evaluation Details</Typography>
                                                    </Box>
                                                </AccordionSummary>
                                                <AccordionDetails>
                                                    {renderConditionCheck()}
                                                </AccordionDetails>
                                            </Accordion>
                                        )}
                                    </motion.div>
                                ) : (
                                    <Box sx={{ textAlign: 'center', py: 4 }}>
                                        <Typography variant="body1" color="text.secondary" gutterBottom>
                                            No test results yet
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Enter test data and click "Test Rule" to see results
                                        </Typography>
                                    </Box>
                                )}
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>

                {/* Test Statistics */}
                {testResults && (
                    <Paper variant="outlined" sx={{ p: 2, mt: 3 }}>
                        <Typography variant="subtitle2" gutterBottom>
                            Test Statistics
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={6} sm={3}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Typography variant="h6" color="primary.main">
                                        {testResults.evaluation_time || 0}ms
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        Evaluation Time
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={6} sm={3}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Typography variant="h6" color={testResults.match ? 'success.main' : 'error.main'}>
                                        {testResults.match ? 'YES' : 'NO'}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        Match Result
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={6} sm={3}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Typography variant="h6">
                                        {format(new Date(testResults.timestamp || new Date()), 'HH:mm:ss')}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        Test Time
                                    </Typography>
                                </Box>
                            </Grid>
                            <Grid item xs={6} sm={3}>
                                <Box sx={{ textAlign: 'center' }}>
                                    <Typography variant="h6">
                                        {testResults.condition_checks?.length || 0}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        Conditions Checked
                                    </Typography>
                                </Box>
                            </Grid>
                        </Grid>
                    </Paper>
                )}

                {/* Quick Test Examples */}
                <Paper variant="outlined" sx={{ p: 2, mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                        Quick Test Examples
                    </Typography>
                    <Grid container spacing={1}>
                        {[
                            { label: 'Stock Price Drop', data: { price: 185, volume: 15000000 } },
                            { label: 'High Volume', data: { price: 200, volume: 20000000 } },
                            { label: 'News Alert', data: { sentiment: -0.8, headline: 'Breaking negative news' } },
                            { label: 'System Alert', data: { cpu_usage: 95, memory_usage: 90 } }
                        ].map((example, index) => (
                            <Grid item key={index}>
                                <Chip
                                    label={example.label}
                                    onClick={() => setTestData(JSON.stringify(example.data, null, 2))}
                                    variant="outlined"
                                />
                            </Grid>
                        ))}
                    </Grid>
                </Paper>
            </Paper>

            {/* Historical Tests */}
            {false && ( // Feature placeholder
                <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                        <History sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Previous Tests
                    </Typography>
                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Time</TableCell>
                                    <TableCell>Result</TableCell>
                                    <TableCell>Data Preview</TableCell>
                                    <TableCell>Duration</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {/* Placeholder for historical tests */}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            )}
        </Box>
    );
};

export default RuleTester;