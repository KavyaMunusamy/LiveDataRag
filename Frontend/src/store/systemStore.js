import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useSystemStore = create(
    persist(
        (set, get) => ({
            // System state
            isActive: true,
            wsConnected: false,
            lastError: null,
            
            // Data
            dataStreams: [],
            actions: [],
            queries: [],
            
            // Settings
            autoConfirmActions: false,
            notificationPreferences: {
                email: true,
                push: true,
                sound: true
            },
            
            // Actions
            toggleSystem: () => set(state => ({ isActive: !state.isActive })),
            
            addDataStream: (stream) => set(state => ({
                dataStreams: [stream, ...state.dataStreams.slice(0, 49)]
            })),
            
            addAction: (action) => set(state => ({
                actions: [action, ...state.actions.slice(0, 99)]
            })),
            
            addQuery: (query) => set(state => ({
                queries: [query, ...state.queries.slice(0, 49)]
            })),
            
            updateSystemStatus: (status) => set({ ...status }),
            
            setAutoConfirm: (value) => set({ autoConfirmActions: value }),
            
            updateNotificationPrefs: (prefs) => set(state => ({
                notificationPreferences: { ...state.notificationPreferences, ...prefs }
            })),
            
            clearHistory: () => set({ actions: [], queries: [], dataStreams: [] }),
            
            // Computed values
            getStats: () => {
                const state = get();
                return {
                    totalActions: state.actions.length,
                    totalQueries: state.queries.length,
                    totalDataPoints: state.dataStreams.length,
                    successRate: state.actions.length > 0 
                        ? (state.actions.filter(a => a.status === 'executed').length / state.actions.length * 100).toFixed(1)
                        : 0
                };
            }
        }),
        {
            name: 'system-store',
            partialize: (state) => ({
                autoConfirmActions: state.autoConfirmActions,
                notificationPreferences: state.notificationPreferences
            })
        }
    )
);