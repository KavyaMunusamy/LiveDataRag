import React from 'react';
import {
    Box,
    CircularProgress,
    LinearProgress,
    Typography,
    Fade,
    Paper,
    Backdrop
} from '@mui/material';
import {
    Timeline,
    DataArray,
    AutoGraph,
    Security
} from '@mui/icons-material';
import PropTypes from 'prop-types';

const LoadingSpinner = ({
    type = 'circular',
    size = 40,
    thickness = 4,
    message = '',
    subMessage = '',
    fullScreen = false,
    overlay = false,
    progress = null, // For determinate progress (0-100)
    icon = null,
    color = 'primary',
    speed = 'normal'
}) => {
    const speedMap = {
        slow: 2,
        normal: 1.5,
        fast: 1
    };

    const iconMap = {
        data: <DataArray />,
        timeline: <Timeline />,
        graph: <AutoGraph />,
        security: <Security />
    };

    const renderSpinner = () => {
        if (type === 'linear') {
            return (
                <Box sx={{ width: '100%', position: 'relative' }}>
                    <LinearProgress
                        variant={progress !== null ? 'determinate' : 'indeterminate'}
                        value={progress}
                        color={color}
                        sx={{
                            height: 6,
                            borderRadius: 3,
                            '& .MuiLinearProgress-bar': {
                                animationDuration: `${speedMap[speed]}s`
                            }
                        }}
                    />
                    {progress !== null && (
                        <Typography
                            variant="caption"
                            sx={{
                                position: 'absolute',
                                right: 0,
                                top: -20,
                                color: 'text.secondary'
                            }}
                        >
                            {Math.round(progress)}%
                        </Typography>
                    )}
                </Box>
            );
        }

        // Default circular spinner
        return (
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                <CircularProgress
                    size={size}
                    thickness={thickness}
                    color={color}
                    sx={{
                        animationDuration: `${speedMap[speed]}s`
                    }}
                />
                {icon && (
                    <Box
                        sx={{
                            top: 0,
                            left: 0,
                            bottom: 0,
                            right: 0,
                            position: 'absolute',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: `${color}.main`
                        }}
                    >
                        {iconMap[icon] || icon}
                    </Box>
                )}
                {progress !== null && type === 'circular' && (
                    <Box
                        sx={{
                            top: 0,
                            left: 0,
                            bottom: 0,
                            right: 0,
                            position: 'absolute',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        <Typography
                            variant="caption"
                            component="div"
                            color="text.secondary"
                            sx={{ fontSize: size * 0.25 }}
                        >
                            {`${Math.round(progress)}%`}
                        </Typography>
                    </Box>
                )}
            </Box>
        );
    };

    const content = (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 2,
                p: fullScreen ? 0 : 3
            }}
        >
            {renderSpinner()}
            
            {(message || subMessage) && (
                <Box sx={{ textAlign: 'center', maxWidth: 400 }}>
                    {message && (
                        <Typography
                            variant="body1"
                            color="text.primary"
                            gutterBottom
                            sx={{
                                fontWeight: 500,
                                animation: 'pulse 2s infinite'
                            }}
                        >
                            {message}
                        </Typography>
                    )}
                    {subMessage && (
                        <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: 'block' }}
                        >
                            {subMessage}
                        </Typography>
                    )}
                </Box>
            )}
        </Box>
    );

    if (fullScreen) {
        return (
            <Backdrop
                open={true}
                sx={{
                    zIndex: 9999,
                    backgroundColor: overlay ? 'rgba(0, 0, 0, 0.8)' : 'background.paper',
                    flexDirection: 'column'
                }}
            >
                <Fade in={true} timeout={500}>
                    {content}
                </Fade>
            </Backdrop>
        );
    }

    if (overlay) {
        return (
            <Box
                sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    zIndex: 10,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
            >
                <Fade in={true} timeout={300}>
                    {content}
                </Fade>
            </Box>
        );
    }

    return (
        <Paper
            elevation={0}
            sx={{
                p: 4,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: 200,
                bgcolor: 'transparent'
            }}
        >
            <Fade in={true} timeout={500}>
                {content}
            </Fade>
        </Paper>
    );
};

LoadingSpinner.propTypes = {
    type: PropTypes.oneOf(['circular', 'linear']),
    size: PropTypes.number,
    thickness: PropTypes.number,
    message: PropTypes.string,
    subMessage: PropTypes.string,
    fullScreen: PropTypes.bool,
    overlay: PropTypes.bool,
    progress: PropTypes.number,
    icon: PropTypes.oneOf(['data', 'timeline', 'graph', 'security', null]),
    color: PropTypes.oneOf(['primary', 'secondary', 'error', 'warning', 'info', 'success']),
    speed: PropTypes.oneOf(['slow', 'normal', 'fast'])
};

// Specialized loading components
export const DataLoadingSpinner = (props) => (
    <LoadingSpinner
        message="Loading real-time data..."
        subMessage="Connecting to live data streams"
        icon="data"
        color="info"
        {...props}
    />
);

export const SystemLoadingSpinner = (props) => (
    <LoadingSpinner
        message="Initializing system components..."
        subMessage="Starting RAG engine and action systems"
        icon="security"
        color="primary"
        {...props}
    />
);

export const ActionLoadingSpinner = (props) => (
    <LoadingSpinner
        message="Processing action..."
        subMessage="Evaluating and executing autonomous actions"
        icon="timeline"
        color="warning"
        {...props}
    />
);

export const QueryLoadingSpinner = (props) => (
    <LoadingSpinner
        message="Analyzing query..."
        subMessage="Retrieving relevant data and generating insights"
        icon="graph"
        color="success"
        {...props}
    />
);

export default LoadingSpinner;