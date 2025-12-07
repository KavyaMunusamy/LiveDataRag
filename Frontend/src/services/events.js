import { EventEmitter } from 'events';

class EventService extends EventEmitter {
    constructor() {
        super();
        this.setMaxListeners(100); // Allow many listeners
        
        // System events
        this.EVENTS = {
            // System events
            SYSTEM_STATUS_CHANGE: 'system_status_change',
            SYSTEM_ERROR: 'system_error',
            SYSTEM_WARNING: 'system_warning',
            SYSTEM_INFO: 'system_info',
            
            // Data events
            DATA_STREAM_UPDATE: 'data_stream_update',
            DATA_STREAM_ERROR: 'data_stream_error',
            DATA_POINT_RECEIVED: 'data_point_received',
            
            // Action events
            ACTION_TRIGGERED: 'action_triggered',
            ACTION_EXECUTED: 'action_executed',
            ACTION_FAILED: 'action_failed',
            ACTION_CONFIRMATION_REQUIRED: 'action_confirmation_required',
            
            // Query events
            QUERY_SUBMITTED: 'query_submitted',
            QUERY_COMPLETED: 'query_completed',
            QUERY_ERROR: 'query_error',
            
            // Rule events
            RULE_CREATED: 'rule_created',
            RULE_UPDATED: 'rule_updated',
            RULE_DELETED: 'rule_deleted',
            RULE_TRIGGERED: 'rule_triggered',
            
            // User events
            USER_LOGIN: 'user_login',
            USER_LOGOUT: 'user_logout',
            USER_ACTION: 'user_action',
            
            // Notification events
            NOTIFICATION_CREATED: 'notification_created',
            NOTIFICATION_DISMISSED: 'notification_dismissed',
            
            // WebSocket events
            WS_CONNECTED: 'ws_connected',
            WS_DISCONNECTED: 'ws_disconnected',
            WS_ERROR: 'ws_error'
        };
    }

    // System events
    emitSystemStatusChange(status) {
        this.emit(this.EVENTS.SYSTEM_STATUS_CHANGE, {
            timestamp: new Date().toISOString(),
            status
        });
    }

    emitSystemError(error, context = {}) {
        const eventData = {
            timestamp: new Date().toISOString(),
            error: error.message || error,
            stack: error.stack,
            context
        };
        this.emit(this.EVENTS.SYSTEM_ERROR, eventData);
        console.error('System Error:', eventData);
    }

    emitSystemWarning(warning, context = {}) {
        this.emit(this.EVENTS.SYSTEM_WARNING, {
            timestamp: new Date().toISOString(),
            warning,
            context
        });
    }

    emitSystemInfo(message, details = {}) {
        this.emit(this.EVENTS.SYSTEM_INFO, {
            timestamp: new Date().toISOString(),
            message,
            details
        });
    }

    // Data events
    emitDataStreamUpdate(streamId, data) {
        this.emit(this.EVENTS.DATA_STREAM_UPDATE, {
            timestamp: new Date().toISOString(),
            streamId,
            data
        });
    }

    emitDataPointReceived(dataPoint) {
        this.emit(this.EVENTS.DATA_POINT_RECEIVED, {
            timestamp: new Date().toISOString(),
            dataPoint
        });
    }

    // Action events
    emitActionTriggered(action) {
        this.emit(this.EVENTS.ACTION_TRIGGERED, {
            timestamp: new Date().toISOString(),
            action
        });
    }

    emitActionExecuted(action) {
        this.emit(this.EVENTS.ACTION_EXECUTED, {
            timestamp: new Date().toISOString(),
            action
        });
    }

    emitActionConfirmationRequired(action) {
        this.emit(this.EVENTS.ACTION_CONFIRMATION_REQUIRED, {
            timestamp: new Date().toISOString(),
            action
        });
    }

    // Query events
    emitQuerySubmitted(query) {
        this.emit(this.EVENTS.QUERY_SUBMITTED, {
            timestamp: new Date().toISOString(),
            query
        });
    }

    emitQueryCompleted(query, result) {
        this.emit(this.EVENTS.QUERY_COMPLETED, {
            timestamp: new Date().toISOString(),
            query,
            result
        });
    }

    // Rule events
    emitRuleTriggered(rule, context) {
        this.emit(this.EVENTS.RULE_TRIGGERED, {
            timestamp: new Date().toISOString(),
            rule,
            context
        });
    }

    // User events
    emitUserAction(action, details = {}) {
        this.emit(this.EVENTS.USER_ACTION, {
            timestamp: new Date().toISOString(),
            action,
            details
        });
    }

    // WebSocket events
    emitWebSocketConnected() {
        this.emit(this.EVENTS.WS_CONNECTED, {
            timestamp: new Date().toISOString()
        });
    }

    emitWebSocketDisconnected(reason) {
        this.emit(this.EVENTS.WS_DISCONNECTED, {
            timestamp: new Date().toISOString(),
            reason
        });
    }

    // Utility methods
    subscribe(event, callback) {
        this.on(event, callback);
        return () => this.off(event, callback);
    }

    subscribeOnce(event, callback) {
        this.once(event, callback);
    }

    unsubscribe(event, callback) {
        this.off(event, callback);
    }

    // Event logging for debugging
    enableDebugLogging() {
        Object.values(this.EVENTS).forEach(event => {
            this.on(event, (data) => {
                console.log(`[Event: ${event}]`, data);
            });
        });
    }

    // Event history (last 100 events)
    getEventHistory(maxEvents = 100) {
        // This would typically come from a store or state management
        return [];
    }

    // Clear all listeners (use with caution)
    clearAllListeners() {
        Object.values(this.EVENTS).forEach(event => {
            this.removeAllListeners(event);
        });
    }
}

// Create singleton instance
export const eventService = new EventService();

// React hook for event subscription
export const useEventSubscription = (event, callback, dependencies = []) => {
    React.useEffect(() => {
        const unsubscribe = eventService.subscribe(event, callback);
        return () => unsubscribe();
    }, [event, ...dependencies]);
};

export default eventService;