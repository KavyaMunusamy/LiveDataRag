import React from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    Container,
    Alert,
    AlertTitle,
    Stack,
    Divider
} from '@mui/material';
import {
    ErrorOutline,
    Refresh,
    Home,
    ReportProblem,
    Code
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
            errorId: null
        };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Generate error ID for tracking
        const errorId = `ERR_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        this.setState({
            error: error,
            errorInfo: errorInfo,
            errorId: errorId,
            componentStack: errorInfo.componentStack
        });

        // Log error to your error tracking service
        this.logError(error, errorInfo, errorId);
    }

    logError(error, errorInfo, errorId) {
        const errorDetails = {
            errorId,
            message: error?.message,
            stack: error?.stack,
            componentStack: errorInfo?.componentStack,
            url: window.location.href,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        };

        console.error('Application Error:', errorDetails);

        // Send to your backend for logging
        if (process.env.NODE_ENV === 'production') {
            try {
                fetch('/api/v1/monitoring/errors', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(errorDetails)
                }).catch(() => { /* Ignore logging errors */ });
            } catch (e) {
                // Ignore
            }
        }
    }

    handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
            errorId: null
        });
        
        // Force a hard reset of the app
        window.location.reload();
    };

    handleGoHome = () => {
        const navigate = this.props.navigate;
        if (navigate) {
            navigate('/');
        } else {
            window.location.href = '/';
        }
    };

    render() {
        if (this.state.hasError) {
            return (
                <Container maxWidth="md" sx={{ mt: 8, mb: 8 }}>
                    <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
                        <Box sx={{ textAlign: 'center', mb: 4 }}>
                            <ErrorOutline 
                                sx={{ 
                                    fontSize: 80, 
                                    color: 'error.main',
                                    mb: 2 
                                }} 
                            />
                            <Typography variant="h4" component="h1" gutterBottom color="error">
                                Application Error
                            </Typography>
                            <Typography variant="subtitle1" color="text.secondary" paragraph>
                                Something went wrong in the Live Data RAG system
                            </Typography>
                            {this.state.errorId && (
                                <Alert severity="info" sx={{ mb: 2 }}>
                                    <AlertTitle>Error Reference</AlertTitle>
                                    Please reference this ID if contacting support: 
                                    <strong> {this.state.errorId}</strong>
                                </Alert>
                            )}
                        </Box>

                        <Divider sx={{ my: 3 }} />

                        <Stack spacing={3}>
                            {/* Error Details (collapsible for dev) */}
                            {process.env.NODE_ENV === 'development' && (
                                <Box>
                                    <Typography variant="h6" gutterBottom>
                                        <ReportProblem sx={{ mr: 1, verticalAlign: 'middle' }} />
                                        Error Details
                                    </Typography>
                                    <Paper 
                                        variant="outlined" 
                                        sx={{ 
                                            p: 2, 
                                            bgcolor: 'grey.50',
                                            overflow: 'auto',
                                            maxHeight: 200,
                                            fontFamily: 'monospace',
                                            fontSize: '0.875rem'
                                        }}
                                    >
                                        <Typography variant="body2" component="pre">
                                            {this.state.error?.toString()}
                                        </Typography>
                                        <Typography variant="caption" component="pre" color="text.secondary">
                                            {this.state.componentStack}
                                        </Typography>
                                    </Paper>
                                </Box>
                            )}

                            {/* Troubleshooting Steps */}
                            <Box>
                                <Typography variant="h6" gutterBottom>
                                    Troubleshooting Steps
                                </Typography>
                                <Stack spacing={1}>
                                    <Typography variant="body2">
                                        1. Check your internet connection
                                    </Typography>
                                    <Typography variant="body2">
                                        2. Refresh the page to reload the application
                                    </Typography>
                                    <Typography variant="body2">
                                        3. Clear browser cache if problem persists
                                    </Typography>
                                    <Typography variant="body2">
                                        4. Try accessing from a different browser
                                    </Typography>
                                </Stack>
                            </Box>

                            {/* Action Buttons */}
                            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 3 }}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    startIcon={<Refresh />}
                                    onClick={this.handleReset}
                                    size="large"
                                >
                                    Reload Application
                                </Button>
                                
                                <Button
                                    variant="outlined"
                                    color="primary"
                                    startIcon={<Home />}
                                    onClick={this.handleGoHome}
                                    size="large"
                                >
                                    Go to Dashboard
                                </Button>
                                
                                {process.env.NODE_ENV === 'development' && (
                                    <Button
                                        variant="outlined"
                                        color="secondary"
                                        startIcon={<Code />}
                                        onClick={() => {
                                            console.error('Full error details:', {
                                                error: this.state.error,
                                                errorInfo: this.state.errorInfo
                                            });
                                        }}
                                        size="large"
                                    >
                                        Console Details
                                    </Button>
                                )}
                            </Box>

                            {/* System Status */}
                            <Alert severity="warning" sx={{ mt: 2 }}>
                                <AlertTitle>System Status</AlertTitle>
                                While this error is being resolved, some features may be unavailable.
                                Real-time data updates will continue in the background.
                            </Alert>
                        </Stack>

                        {/* Footer */}
                        <Box sx={{ mt: 4, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                            <Typography variant="caption" color="text.secondary" align="center">
                                Live Data RAG System v{process.env.REACT_APP_VERSION || '1.0.0'} • 
                                If this error persists, please contact support with the error reference.
                            </Typography>
                        </Box>
                    </Paper>
                </Container>
            );
        }

        return this.props.children;
    }
}

// Higher-order component to use with React Router
export default function ErrorBoundaryWithRouter(props) {
    const navigate = useNavigate();
    return <ErrorBoundary {...props} navigate={navigate} />;
}

// Also export the raw class for non-router usage
export { ErrorBoundary as BaseErrorBoundary };