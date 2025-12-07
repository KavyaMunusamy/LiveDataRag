import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    TableSortLabel,
    IconButton,
    Chip,
    Switch,
    Tooltip,
    Menu,
    MenuItem,
    Button,
    Stack,
    TextField,
    InputAdornment,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
    LinearProgress,
    Grid,
    Card,
    CardContent,
    Badge
} from '@mui/material';
import {
    Edit,
    Delete,
    PlayArrow,
    MoreVert,
    Search,
    FilterList,
    Download,
    Visibility,
    VisibilityOff,
    History,
    ContentCopy,
    CheckCircle,
    Error,
    Warning,
    Pause,
    Schedule,
    TrendingUp,
    DataArray,
    Security,
    Refresh,
    Sort
} from '@mui/icons-material';
import { format, parseISO } from 'date-fns';
import { motion } from 'framer-motion';

const RuleList = ({ 
    rules = [], 
    onEdit, 
    onDelete, 
    onToggle,
    onTest,
    onDuplicate,
    isLoading = false
}) => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('all');
    const [sortField, setSortField] = useState('last_triggered');
    const [sortDirection, setSortDirection] = useState('desc');
    const [anchorEl, setAnchorEl] = useState(null);
    const [selectedRule, setSelectedRule] = useState(null);
    const [deleteDialog, setDeleteDialog] = useState(false);

    const filters = [
        { value: 'all', label: 'All Rules' },
        { value: 'active', label: 'Active Only' },
        { value: 'inactive', label: 'Inactive Only' },
        { value: 'error', label: 'With Errors' },
        { value: 'scheduled', label: 'Scheduled' }
    ];

    const ruleTypes = {
        financial: { color: 'primary', icon: <TrendingUp /> },
        monitoring: { color: 'warning', icon: <Security /> },
        data: { color: 'success', icon: <DataArray /> },
        system: { color: 'info', icon: <Schedule /> }
    };

    const filteredRules = rules
        .filter(rule => {
            const matchesSearch = searchTerm === '' || 
                rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                rule.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                rule.condition?.type?.toLowerCase().includes(searchTerm.toLowerCase());
            
            const matchesFilter = 
                filter === 'all' ||
                (filter === 'active' && rule.enabled) ||
                (filter === 'inactive' && !rule.enabled) ||
                (filter === 'error' && rule.error_count > 0) ||
                (filter === 'scheduled' && rule.schedule?.enabled);
            
            return matchesSearch && matchesFilter;
        })
        .sort((a, b) => {
            const aVal = a[sortField];
            const bVal = b[sortField];
            
            if (sortField === 'last_triggered' || sortField === 'created_at') {
                return sortDirection === 'desc' 
                    ? new Date(bVal) - new Date(aVal)
                    : new Date(aVal) - new Date(bVal);
            }
            
            if (typeof aVal === 'string' && typeof bVal === 'string') {
                return sortDirection === 'desc' 
                    ? bVal.localeCompare(aVal)
                    : aVal.localeCompare(bVal);
            }
            
            return sortDirection === 'desc' 
                ? (bVal || 0) - (aVal || 0)
                : (aVal || 0) - (bVal || 0);
        });

    const paginatedRules = filteredRules.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage
    );

    const handleSort = (field) => {
        if (sortField === field) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection('desc');
        }
    };

    const handleMenuOpen = (event, rule) => {
        setAnchorEl(event.currentTarget);
        setSelectedRule(rule);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedRule(null);
    };

    const handleDelete = () => {
        if (selectedRule) {
            onDelete?.(selectedRule.id);
            setDeleteDialog(false);
            handleMenuClose();
        }
    };

    const getRuleStatus = (rule) => {
        if (!rule.enabled) {
            return { color: 'default', label: 'Disabled', icon: <VisibilityOff /> };
        }
        if (rule.error_count > 0) {
            return { color: 'error', label: 'Error', icon: <Error /> };
        }
        if (rule.success_rate < 80) {
            return { color: 'warning', label: 'Warning', icon: <Warning /> };
        }
        return { color: 'success', label: 'Active', icon: <CheckCircle /> };
    };

    const RuleRow = ({ rule }) => {
        const status = getRuleStatus(rule);
        const type = ruleTypes[rule.type] || ruleTypes.system;
        
        return (
            <motion.tr
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
            >
                <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Tooltip title={type.icon}>
                            <Box sx={{ color: `${type.color}.main` }}>
                                {type.icon}
                            </Box>
                        </Tooltip>
                        <Box>
                            <Typography variant="body2" fontWeight="medium">
                                {rule.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                {rule.description || 'No description'}
                            </Typography>
                        </Box>
                    </Box>
                </TableCell>
                
                <TableCell>
                    <Chip
                        size="small"
                        icon={status.icon}
                        label={status.label}
                        color={status.color}
                        variant="outlined"
                    />
                </TableCell>
                
                <TableCell>
                    <Chip
                        size="small"
                        label={rule.condition?.type || 'unknown'}
                        variant="outlined"
                    />
                </TableCell>
                
                <TableCell>
                    <Chip
                        size="small"
                        label={rule.action?.type || 'unknown'}
                        color="primary"
                        variant="outlined"
                    />
                </TableCell>
                
                <TableCell align="center">
                    <Badge 
                        badgeContent={rule.trigger_count || 0} 
                        color="primary"
                        max={999}
                    >
                        <Typography variant="body2">
                            {rule.success_rate?.toFixed(1) || '0'}%
                        </Typography>
                    </Badge>
                </TableCell>
                
                <TableCell>
                    <Typography variant="caption" color="text.secondary">
                        {rule.last_triggered 
                            ? format(parseISO(rule.last_triggered), 'MM/dd HH:mm')
                            : 'Never'
                        }
                    </Typography>
                </TableCell>
                
                <TableCell>
                    <Stack direction="row" spacing={1}>
                        <Switch
                            size="small"
                            checked={rule.enabled}
                            onChange={() => onToggle?.(rule.id)}
                        />
                        <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => onEdit?.(rule)}>
                                <Edit />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="More actions">
                            <IconButton 
                                size="small" 
                                onClick={(e) => handleMenuOpen(e, rule)}
                            >
                                <MoreVert />
                            </IconButton>
                        </Tooltip>
                    </Stack>
                </TableCell>
            </motion.tr>
        );
    };

    if (isLoading) {
        return (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                    Loading Rules...
                </Typography>
                <LinearProgress sx={{ my: 2 }} />
            </Paper>
        );
    }

    if (rules.length === 0) {
        return (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Rules Created
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                    Create your first rule to automate actions based on real-time data
                </Typography>
                <Button variant="contained" startIcon={<PlayArrow />}>
                    Create First Rule
                </Button>
            </Paper>
        );
    }

    return (
        <Box>
            {/* Header */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <TextField
                                placeholder="Search rules..."
                                size="small"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                InputProps={{
                                    startAdornment: (
                                        <InputAdornment position="start">
                                            <Search />
                                        </InputAdornment>
                                    ),
                                }}
                                sx={{ minWidth: 300 }}
                            />
                            
                            <Tooltip title="Filter">
                                <IconButton size="small">
                                    <FilterList />
                                </IconButton>
                            </Tooltip>
                        </Box>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                            <Button
                                size="small"
                                startIcon={<Refresh />}
                                onClick={() => console.log('Refresh')}
                            >
                                Refresh
                            </Button>
                            <Button
                                size="small"
                                startIcon={<Download />}
                                onClick={() => console.log('Export')}
                            >
                                Export
                            </Button>
                        </Box>
                    </Grid>
                </Grid>
            </Paper>

            {/* Stats Summary */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} sm={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="primary.main">
                                {rules.length}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                Total Rules
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="success.main">
                                {rules.filter(r => r.enabled).length}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                Active Rules
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="warning.main">
                                {rules.filter(r => r.error_count > 0).length}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                With Errors
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                    <Card>
                        <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="info.main">
                                {rules.filter(r => r.trigger_count > 0).length}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                Triggered Today
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Rules Table */}
            <Paper>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>
                                    <TableSortLabel
                                        active={sortField === 'name'}
                                        direction={sortDirection}
                                        onClick={() => handleSort('name')}
                                    >
                                        Rule Name
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell>
                                    <TableSortLabel
                                        active={sortField === 'enabled'}
                                        direction={sortDirection}
                                        onClick={() => handleSort('enabled')}
                                    >
                                        Status
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell>Condition</TableCell>
                                <TableCell>Action</TableCell>
                                <TableCell align="center">
                                    <TableSortLabel
                                        active={sortField === 'success_rate'}
                                        direction={sortDirection}
                                        onClick={() => handleSort('success_rate')}
                                    >
                                        Success Rate
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell>
                                    <TableSortLabel
                                        active={sortField === 'last_triggered'}
                                        direction={sortDirection}
                                        onClick={() => handleSort('last_triggered')}
                                    >
                                        Last Triggered
                                    </TableSortLabel>
                                </TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {paginatedRules.map((rule) => (
                                <RuleRow key={rule.id} rule={rule} />
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
                
                <TablePagination
                    rowsPerPageOptions={[5, 10, 25, 50]}
                    component="div"
                    count={filteredRules.length}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={(_, newPage) => setPage(newPage)}
                    onRowsPerPageChange={(e) => {
                        setRowsPerPage(parseInt(e.target.value, 10));
                        setPage(0);
                    }}
                />
            </Paper>

            {/* Rule Actions Menu */}
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
            >
                <MenuItem onClick={() => {
                    onTest?.(selectedRule);
                    handleMenuClose();
                }}>
                    <PlayArrow sx={{ mr: 1 }} />
                    Test Rule
                </MenuItem>
                <MenuItem onClick={() => {
                    onDuplicate?.(selectedRule);
                    handleMenuClose();
                }}>
                    <ContentCopy sx={{ mr: 1 }} />
                    Duplicate Rule
                </MenuItem>
                <MenuItem onClick={() => {
                    console.log('View history:', selectedRule);
                    handleMenuClose();
                }}>
                    <History sx={{ mr: 1 }} />
                    View History
                </MenuItem>
                <MenuItem 
                    onClick={() => {
                        setDeleteDialog(true);
                    }}
                    sx={{ color: 'error.main' }}
                >
                    <Delete sx={{ mr: 1 }} />
                    Delete Rule
                </MenuItem>
            </Menu>

            {/* Delete Confirmation Dialog */}
            <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
                <DialogTitle>Delete Rule</DialogTitle>
                <DialogContent>
                    <Alert severity="warning" sx={{ mb: 2 }}>
                        Are you sure you want to delete "{selectedRule?.name}"?
                        This action cannot be undone.
                    </Alert>
                    <Typography variant="body2" color="text.secondary">
                        This rule has been triggered {selectedRule?.trigger_count || 0} times.
                        Last triggered: {selectedRule?.last_triggered 
                            ? format(parseISO(selectedRule.last_triggered), 'PPpp')
                            : 'Never'
                        }
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
                    <Button 
                        onClick={handleDelete} 
                        color="error"
                        variant="contained"
                    >
                        Delete Rule
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default RuleList;