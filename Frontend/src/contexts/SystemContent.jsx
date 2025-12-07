import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { wsService } from '../services/websocket';
import { apiService } from '../services/api';
import { useSnackbar } from 'notistack';

const SystemContext = createContext(null);

export const useSystem = () => {
    const context = useContext(SystemContext);
    if (!context) {
        throw new Error('useSystem must be used within SystemProvider');
    }
    return context;
};

export const SystemProvider = ({ children }) => {
    const [systemStatus, setSystemStatus] = useState({
        isActive: true,
        lastUpdated: new Date().toISOString(),
        lastAction: null,
        components: {
            dataPipeline: 'healthy',
            ragEngine: 'healthy',
            actionEngine: 'healthy',
            vectorStore: 'healthy'
        },
        metrics: {
            queryCount: 0,
            actionCount: 0,
            avgLatency: 0,
            errorRate: 0
        }
    });

    const [dataStreams, setDataStreams] = useState([]);
    const [actions, setActions] = useState([]);
    const [queries, setQueries] = useState([]);
    const [rules, setRules] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState([]);
    const { enqueueSnackbar } = useSnackbar();

    // Initialize WebSocket connection
    useEffect(() => {
        wsService.connect();

        return () => {
            wsService.disconnect();
        };
    }, []);

    // Load initial data
    useEffect(() => {
        loadInitialData();
        
        // Refresh data every 30 seconds
        const interval = setInterval(loadInitialData, 30000);
        
        return () => clearInterval(interval);
    }, []);

    const loadInitialData = async () => {
        try {
            setIsLoading(true);
            
            const [streamsData, actionsData, rulesData] = await Promise.all([
                apiService.getDataStreams(),
                apiService.getActionHistory(50),
                apiService.getRules()
            ]);
            
            setDataStreams(streamsData.data || []);
            setActions(actionsData || []);
            setRules(rulesData || []);
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            enqueueSnackbar('Failed to load system data', { variant: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    // WebSocket event handlers
    useEffect(() => {
        const handleDataUpdate = (data) => {
            setDataStreams(prev => {
                const index = prev.findIndex(s => s.id === data.id);
                if (index >= 0) {
                    const updated = [...prev];
                    updated[index] = { ...updated[index], ...data };
                    return updated;
                }
                return [data, ...prev.slice(0, 49)]; // Keep only 50 latest
            });
        };

        const handleActionExecuted = (action) => {
            setActions(prev => [action, ...prev.slice(0, 99)]); // Keep only 100 latest
            
            // Update system status
            setSystemStatus(prev => ({
                ...prev,
                lastAction: action,
                lastUpdated: new Date().toISOString(),
                metrics: {
                    ...prev.metrics,
                    actionCount: prev.metrics.actionCount + 1
                }
            }));

            // Show notification
            if (action.status === 'executed') {
                enqueueSnackbar(`Action executed: ${action.action_type}`, { 
                    variant: 'success',
                    autoHideDuration: 3000 
                });
            } else if (action.status === 'failed') {
                enqueueSnackbar(`Action failed: ${action.error}`, { 
                    variant: 'error',
                    autoHideDuration: 5000 
                });
            }
        };

        const handleSystemStatus = (status) => {
            setSystemStatus(prev => ({ ...prev, ...status }));
        };

        // Subscribe to WebSocket events
        // Note: Actual subscription depends on your WebSocket implementation
        return () => {
            // Cleanup subscriptions
        };
    }, [enqueueSnackbar]);

    const toggleSystem = async () => {
        try {
            const newStatus = !systemStatus.isActive;
            
            // Update backend status
            await apiService.updateSystemStatus({ active: newStatus });
            
            setSystemStatus(prev => ({
                ...prev,
                isActive: newStatus,
                lastUpdated: new Date().toISOString()
            }));
            
            enqueueSnackbar(
                `System ${newStatus ? 'activated' : 'paused'}`,
                { variant: newStatus ? 'success' : 'warning' }
            );
            
        } catch (error) {
            console.error('Failed to toggle system:', error);
            enqueueSnackbar('Failed to update system status', { variant: 'error' });
        }
    };

    const processQuery = async (queryData) => {
        try {
            setIsLoading(true);
            
            const response = await apiService.processQuery(queryData.query, {
                context_type: queryData.context_type,
                time_range: queryData.time_range,
                safety_level: queryData.safety_level
            });
            
            setQueries(prev => [{
                ...queryData,
                response: response.data,
                timestamp: new Date().toISOString()
            }, ...prev.slice(0, 49)]);
            
            // Update metrics
            setSystemStatus(prev => ({
                ...prev,
                metrics: {
                    ...prev.metrics,
                    queryCount: prev.metrics.queryCount + 1
                }
            }));
            
            return response.data;
            
        } catch (error) {
            console.error('Query processing failed:', error);
            enqueueSnackbar('Failed to process query', { variant: 'error' });
            throw error;
        } finally {
            setIsLoading(false);
        }
    };

    const confirmAction = async (actionId, confirm = true) => {
        try {
            const response = await apiService.confirmAction(actionId, confirm);
            
            if (response.success) {
                enqueueSnackbar(
                    `Action ${confirm ? 'confirmed' : 'rejected'}`,
                    { variant: 'success' }
                );
            }
            
            return response;
            
        } catch (error) {
            console.error('Action confirmation failed:', error);
            enqueueSnackbar('Failed to confirm action', { variant: 'error' });
            throw error;
        }
    };

    const createRule = async (ruleData) => {
        try {
            const response = await apiService.createRule(ruleData);
            
            setRules(prev => [response.data, ...prev]);
            enqueueSnackbar('Rule created successfully', { variant: 'success' });
            
            return response.data;
            
        } catch (error) {
            console.error('Rule creation failed:', error);
            enqueueSnackbar('Failed to create rule', { variant: 'error' });
            throw error;
        }
    };

    const updateRule = async (ruleId, updates) => {
        try {
            const response = await apiService.updateRule(ruleId, updates);
            
            setRules(prev => prev.map(rule => 
                rule.id === ruleId ? { ...rule, ...updates } : rule
            ));
            
            enqueueSnackbar('Rule updated successfully', { variant: 'success' });
            
            return response.data;
            
        } catch (error) {
            console.error('Rule update failed:', error);
            enqueueSnackbar('Failed to update rule', { variant: 'error' });
            throw error;
        }
    };

    const deleteRule = async (ruleId) => {
        try {
            await apiService.deleteRule(ruleId);
            
            setRules(prev => prev.filter(rule => rule.id !== ruleId));
            enqueueSnackbar('Rule deleted successfully', { variant: 'success' });
            
        } catch (error) {
            console.error('Rule deletion failed:', error);
            enqueueSnackbar('Failed to delete rule', { variant: 'error' });
            throw error;
        }
    };

    const testRule = async (rule, testData) => {
        try {
            const response = await apiService.testRule({
                rule,
                test_data: testData
            });
            
            return response.data;
            
        } catch (error) {
            console.error('Rule test failed:', error);
            enqueueSnackbar('Failed to test rule', { variant: 'error' });
            throw error;
        }
    };

    const refreshData = useCallback(() => {
        loadInitialData();
        enqueueSnackbar('Data refreshed', { variant: 'info' });
    }, [enqueueSnackbar]);

    const clearErrors = () => {
        setErrors([]);
    };

    const addError = (error) => {
        setErrors(prev => [error, ...prev.slice(0, 9)]); // Keep only 10 latest errors
        enqueueSnackbar(error.message, { variant: 'error' });
    };

    const value = {
        // State
        systemStatus,
        dataStreams,
        actions,
        queries,
        rules,
        isLoading,
        errors,
        
        // Actions
        toggleSystem,
        processQuery,
        confirmAction,
        createRule,
        updateRule,
        deleteRule,
        testRule,
        refreshData,
        clearErrors,
        addError,
        
        // WebSocket status
        wsConnected: wsService.isConnected()
    };

    return (
        <SystemContext.Provider value={value}>
            {children}
        </SystemContext.Provider>
    );
};