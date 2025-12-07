import React, { useState, useMemo } from 'react';
import {
    Box,
    Paper,
    Typography,
    Chip,
    IconButton,
    Tooltip,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TableSortLabel,
    TablePagination,
    TextField,
    InputAdornment,
    MenuItem,
    Select,
    FormControl,
    InputLabel,
    Alert,
    AlertTitle,
    Collapse,
    Button,
    Stack,
    Divider,
    LinearProgress,
    Badge
} from '@mui/material';
import {
    Search,
    FilterList,
    ExpandMore,
    ExpandLess,
    CheckCircle,
    Error,
    Warning,
    Info,
    Pending,
    PlayArrow,
    Block,
    Refresh,
    Download,
    Visibility,
    MoreVert,
    Schedule,
    DoneAll,
    Cancel
} from '@mui/icons-material';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import PropTypes from 'prop-types';

const ActionLog = ({ actions = [], maxHeight = 400, showFilters = true, onActionClick }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [typeFilter, setTypeFilter] = useState('all');
    const [sortField, setSortField] = useState('timestamp');
    const [sortDirection, setSortDirection] = useState('desc');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [expandedAction, setExpandedAction] = useState(null);

    // Action type configuration
    const actionConfig = {
        alert: {
            color: 'info',
            icon: <Info fontSize="small" />,
            label: 'Alert'
        },
        api_call: {
            color: 'primary',
            icon: <PlayArrow fontSize="small" />,
            label: 'API Call'
        },
        data_update: {
            color: 'success',
            icon: <CheckCircle fontSize="small" />,
            label: 'Data Update'
        },
        workflow_trigger: {
            color: 'warning',
            icon: <Schedule fontSize="small" />,
            label: 'Workflow'
        },
        system: {
            color: 'default',
            icon: <MoreVert fontSize="small" />,
            label: 'System'
        }
    };

    // Status configuration
    const statusConfig = {
        executed: {
            color: 'success',
            icon: <DoneAll fontSize="small" />,
            label: 'Executed'
        },
        pending: {
            color: 'warning',
            icon: <Pending fontSize="small" />,
            label: 'Pending'
        },
        failed: {
            color: 'error',
            icon: <Error fontSize="small" />,
            label: 'Failed'
        },
        blocked: {
            color: 'default',
            icon: <Block fontSize="small" />,
            label: 'Blocked'
        },
        requires_confirmation: {
            color: 'info',
            icon: <Warning fontSize="small" />,
            label: 'Needs Confirm'
        },
        rate_limited: {
            color: 'secondary',
            icon: <Schedule fontSize="small" />,
            label: 'Rate Limited'
        }
    };

    // Filter and sort actions
    const filteredActions = useMemo(() => {
        return actions.filter(action => {
            // Search filter
            const matchesSearch = searchTerm === '' || 
                action.type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                action.status?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                action.reason?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                JSON.stringify(action.parameters || {}).toLowerCase().includes(searchTerm.toLowerCase());

            // Status filter
            const matchesStatus = statusFilter === 'all' || action.status === statusFilter;
            
            // Type filter
            const matchesType = typeFilter === 'all' || action.type === typeFilter;

            return matchesSearch && matchesStatus && matchesType;
        }).sort((a, b) => {
            const aValue = a[sortField];
            const bValue = b[sortField];
            
            if (sortField === 'timestamp') {
                return sortDirection === 'desc' 
                    ? new Date(bValue) - new Date(aValue)
                    : new Date(aValue) - new Date(bValue);
            }
            
            if (typeof aValue === 'string' && typeof bValue === 'string') {
                return sortDirection === 'desc'
                    ? bValue.localeCompare(aValue)
                    : aValue.localeCompare(bValue);
            }
            
            return sortDirection === 'desc' 
                ? (bValue || 0) - (aValue || 0)
                : (aValue || 0) - (bValue || 0);
        });
    }, [actions, searchTerm, statusFilter, typeFilter, sortField, sortDirection]);

    // Pagination
    const paginatedActions = useMemo(() => {
        const start = page * rowsPerPage;
        return filteredActions.slice(start, start + rowsPerPage);
    }, [filteredActions, page, rowsPerPage]);

    // Statistics
    const stats = useMemo(() => {
        const total = actions.length;
        const executed = actions.filter(a => a.status === 'executed').length;
        const failed = actions.filter(a => a.status === 'failed').length;
        const pending = actions.filter(a => a.status === 'pending' || a.status === 'requires_confirmation').length;
        
        return {
            total,
            executed,
            failed,
            pending,
            successRate: total > 0 ? (executed / total * 100).toFixed(1) : 0
        };
    }, [actions]);

    const handleSort = (field) => {
        if (sortField === field) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection('desc');
        }
    };

    const handleExpand = (actionId) => {
        setExpandedAction(expandedAction === actionId ? null : actionId);
    };

    const handleExport = () => {
        const csvContent = [
            ['ID', 'Type', 'Status', 'Timestamp', 'Reason', 'Parameters'],
            ...filteredActions.map(action => [
                action.action_id || action.id,
                action.type,
                action.status,
                action.timestamp,
                action.reason || '',
                JSON.stringify(action.parameters || {})
            ])
        ].map(row => row.join(',')).join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `action-log-${format(new Date(), 'yyyy-MM-dd-HHmm')}.csv`;
        a.click();
    };

    const renderActionDetails = (action) => {
        if (!expandedAction === action.action_id) return null;

        return (
            <TableRow>
                <TableCell colSpan={6} sx={{ backgroundColor: 'grey.50', p: 0 }}>
                    <Collapse in={expandedAction === action.action_id} timeout="auto" unmountOnExit>
                        <Box sx={{ p: 3 }}>
                            <Stack spacing={2}>
                                <Typography variant="subtitle2" color="text.secondary">
                                    Action Details
                                </Typography>
                                
                                <Divider />
                                
                                <Box>
                                    <Typography variant="caption" color="text.secondary">
                                        Action ID
                                    </Typography>
                                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                        {action.action_id || action.id}
                                    </Typography>
                                </Box>
                                
                                {action.reason && (
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">
                                            Reason
                                        </Typography>
                                        <Typography variant="body2">
                                            {action.reason}
                                        </Typography>
                                    </Box>
                                )}
                                
                                {action.parameters && Object.keys(action.parameters).length > 0 && (
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">
                                            Parameters
                                        </Typography>
                                        <Paper 
                                            variant="outlined" 
                                            sx={{ 
                                                p: 2, 
                                                mt: 0.5,
                                                bgcolor: 'background.default',
                                                fontFamily: 'monospace',
                                                fontSize: '0.75rem',
                                                maxHeight: 200,
                                                overflow: 'auto'
                                            }}
                                        >
                                            <pre style={{ margin: 0 }}>
                                                {JSON.stringify(action.parameters, null, 2)}
                                            </pre>
                                        </Paper>
                                    </Box>
                                )}
                                
                                {action.result && (
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">
                                            Result
                                        </Typography>
                                        <Paper 
                                            variant="outlined" 
                                            sx={{ 
                                                p: 2, 
                                                mt: 0.5,
                                                bgcolor: 'success.light',
                                                color: 'success.contrastText'
                                            }}
                                        >
                                            <Typography variant="body2">
                                                {typeof action.result === 'string' 
                                                    ? action.result 
                                                    : JSON.stringify(action.result, null, 2)}
                                            </Typography>
                                        </Paper>
                                    </Box>
                                )}
                                
                                {action.error && (
                                    <Box>
                                        <Typography variant="caption" color="text.secondary">
                                            Error
                                        </Typography>
                                        <Alert severity="error" sx={{ mt: 0.5 }}>
                                            <AlertTitle>Action Failed</AlertTitle>
                                            {action.error}
                                        </Alert>
                                    </Box>
                                )}
                                
                                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                                    <Button
                                        size="small"
                                        startIcon={<Visibility />}
                                        onClick={() => onActionClick?.(action)}
                                    >
                                        View Context
                                    </Button>
                                    <Button
                                        size="small"
                                        startIcon={<Refresh />}
                                        onClick={() => console.log('Retry action:', action)}
                                        disabled={action.status === 'executed'}
                                    >
                                        Retry
                                    </Button>
                                </Box>
                            </Stack>
                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>
        );
    };

    if (actions.length === 0) {
        return (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary" paragraph>
                    No actions have been executed yet
                </Typography>
                <Typography variant="caption" color="text.secondary">
                    Actions will appear here when the system processes queries and makes decisions
                </Typography>
            </Paper>
        );
    }

    return (
        <Box>
            {/* Header and Stats */}
            <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                        Action Log
                        <Badge 
                            badgeContent={stats.total} 
                            color="primary" 
                            sx={{ ml: 2 }}
                        />
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Export to CSV">
                            <IconButton onClick={handleExport} size="small">
                                <Download />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Refresh">
                            <IconButton onClick={() => window.location.reload()} size="small">
                                <Refresh />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Box>

                {/* Statistics Bar */}
                <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                    <Stack direction="row" spacing={3} alignItems="center">
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Success Rate
                            </Typography>
                            <Typography variant="h6" color="success.main">
                                {stats.successRate}%
                            </Typography>
                        </Box>
                        <Divider orientation="vertical" flexItem />
                        <Stack direction="row" spacing={4}>
                            <Box>
                                <Chip 
                                    size="small" 
                                    icon={<CheckCircle />}
                                    label={stats.executed}
                                    color="success"
                                    variant="outlined"
                                />
                                <Typography variant="caption" display="block" color="text.secondary">
                                    Executed
                                </Typography>
                            </Box>
                            <Box>
                                <Chip 
                                    size="small" 
                                    icon={<Pending />}
                                    label={stats.pending}
                                    color="warning"
                                    variant="outlined"
                                />
                                <Typography variant="caption" display="block" color="text.secondary">
                                    Pending
                                </Typography>
                            </Box>
                            <Box>
                                <Chip 
                                    size="small" 
                                    icon={<Error />}
                                    label={stats.failed}
                                    color="error"
                                    variant="outlined"
                                />
                                <Typography variant="caption" display="block" color="text.secondary">
                                    Failed
                                </Typography>
                            </Box>
                        </Stack>
                        <Box sx={{ flexGrow: 1 }}>
                            <LinearProgress 
                                variant="determinate" 
                                value={stats.successRate} 
                                color="success"
                                sx={{ height: 6, borderRadius: 3 }}
                            />
                        </Box>
                    </Stack>
                </Paper>
            </Box>

            {/* Filters */}
            {showFilters && (
                <Paper sx={{ p: 2, mb: 2 }}>
                    <Stack direction="row" spacing={2} alignItems="center">
                        <TextField
                            placeholder="Search actions..."
                            size="small"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <Search fontSize="small" />
                                    </InputAdornment>
                                ),
                            }}
                            sx={{ flexGrow: 1 }}
                        />
                        
                        <FormControl size="small" sx={{ minWidth: 150 }}>
                            <InputLabel>Status</InputLabel>
                            <Select
                                value={statusFilter}
                                label="Status"
                                onChange={(e) => setStatusFilter(e.target.value)}
                            >
                                <MenuItem value="all">All Statuses</MenuItem>
                                {Object.entries(statusConfig).map(([key, config]) => (
                                    <MenuItem key={key} value={key}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            {config.icon}
                                            {config.label}
                                        </Box>
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                        
                        <FormControl size="small" sx={{ minWidth: 150 }}>
                            <InputLabel>Type</InputLabel>
                            <Select
                                value={typeFilter}
                                label="Type"
                                onChange={(e) => setTypeFilter(e.target.value)}
                            >
                                <MenuItem value="all">All Types</MenuItem>
                                {Object.entries(actionConfig).map(([key, config]) => (
                                    <MenuItem key={key} value={key}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            {config.icon}
                                            {config.label}
                                        </Box>
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Stack>
                </Paper>
            )}

            {/* Actions Table */}
            <TableContainer 
                component={Paper} 
                variant="outlined"
                sx={{ maxHeight }}
            >
                <Table stickyHeader size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell sx={{ width: 50 }}></TableCell>
                            <TableCell>
                                <TableSortLabel
                                    active={sortField === 'type'}
                                    direction={sortDirection}
                                    onClick={() => handleSort('type')}
                                >
                                    Type
                                </TableSortLabel>
                            </TableCell>
                            <TableCell>
                                <TableSortLabel
                                    active={sortField === 'status'}
                                    direction={sortDirection}
                                    onClick={() => handleSort('status')}
                                >
                                    Status
                                </TableSortLabel>
                            </TableCell>
                            <TableCell>
                                <TableSortLabel
                                    active={sortField === 'timestamp'}
                                    direction={sortDirection}
                                    onClick={() => handleSort('timestamp')}
                                >
                                    Timestamp
                                </TableSortLabel>
                            </TableCell>
                            <TableCell>Reason</TableCell>
                            <TableCell align="right">Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {paginatedActions.map((action) => {
                            const actionType = actionConfig[action.type] || actionConfig.system;
                            const actionStatus = statusConfig[action.status] || statusConfig.pending;
                            
                            return (
                                <React.Fragment key={action.action_id || action.id}>
                                    <TableRow 
                                        hover
                                        sx={{ 
                                            cursor: 'pointer',
                                            '&:hover': { backgroundColor: 'action.hover' }
                                        }}
                                    >
                                        <TableCell>
                                            <IconButton
                                                size="small"
                                                onClick={() => handleExpand(action.action_id || action.id)}
                                            >
                                                {expandedAction === action.action_id ? 
                                                    <ExpandLess /> : 
                                                    <ExpandMore />
                                                }
                                            </IconButton>
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                size="small"
                                                icon={actionType.icon}
                                                label={actionType.label}
                                                color={actionType.color}
                                                variant="outlined"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                size="small"
                                                icon={actionStatus.icon}
                                                label={actionStatus.label}
                                                color={actionStatus.color}
                                                variant="filled"
                                                sx={{ color: 'white' }}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Tooltip 
                                                title={format(parseISO(action.timestamp), 'PPpp')}
                                            >
                                                <Typography variant="body2">
                                                    {formatDistanceToNow(parseISO(action.timestamp), { addSuffix: true })}
                                                </Typography>
                                            </Tooltip>
                                        </TableCell>
                                        <TableCell>
                                            <Typography 
                                                variant="body2" 
                                                noWrap
                                                sx={{ maxWidth: 200 }}
                                            >
                                                {action.reason || 'No reason provided'}
                                            </Typography>
                                        </TableCell>
                                        <TableCell align="right">
                                            <Tooltip title="View Details">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleExpand(action.action_id || action.id)}
                                                >
                                                    <Visibility fontSize="small" />
                                                </IconButton>
                                            </Tooltip>
                                        </TableCell>
                                    </TableRow>
                                    {renderActionDetails(action)}
                                </React.Fragment>
                            );
                        })}
                    </TableBody>
                </Table>
            </TableContainer>

            {/* Pagination */}
            <TablePagination
                component="div"
                count={filteredActions.length}
                page={page}
                onPageChange={(_, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => {
                    setRowsPerPage(parseInt(e.target.value, 10));
                    setPage(0);
                }}
                rowsPerPageOptions={[5, 10, 25, 50]}
                sx={{ borderTop: 1, borderColor: 'divider' }}
            />
        </Box>
    );
};

ActionLog.propTypes = {
    actions: PropTypes.arrayOf(PropTypes.shape({
        action_id: PropTypes.string,
        type: PropTypes.string,
        status: PropTypes.string,
        timestamp: PropTypes.string,
        reason: PropTypes.string,
        parameters: PropTypes.object,
        result: PropTypes.any,
        error: PropTypes.string
    })),
    maxHeight: PropTypes.number,
    showFilters: PropTypes.bool,
    onActionClick: PropTypes.func
};

export default ActionLog;