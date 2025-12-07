import { io } from 'socket.io-client';
import { systemStore } from '../store/systemStore';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    if (this.socket && this.connected) return;

    this.socket = io(import.meta.env.VITE_WS_URL || 'ws://localhost:8000', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay
    });

    this.setupEventListeners();
  }

  setupEventListeners() {
    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.connected = true;
      this.reconnectAttempts = 0;
      systemStore.setState({ wsConnected: true });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.connected = false;
      systemStore.setState({ wsConnected: false });
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, try to reconnect
        this.socket.connect();
      }
    });

    this.socket.on('data_update', (data) => {
      systemStore.getState().addDataStream(data);
    });

    this.socket.on('action_executed', (action) => {
      systemStore.getState().addAction(action);
    });

    this.socket.on('system_status', (status) => {
      systemStore.getState().updateSystemStatus(status);
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    this.socket.on('reconnect_attempt', (attempt) => {
      this.reconnectAttempts = attempt;
      console.log(`Reconnect attempt ${attempt}/${this.maxReconnectAttempts}`);
    });

    this.socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed');
      systemStore.setState({ 
        wsConnected: false,
        lastError: 'Failed to reconnect to server'
      });
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
      systemStore.setState({ wsConnected: false });
    }
  }

  emit(event, data) {
    if (this.socket && this.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('Cannot emit, WebSocket not connected');
    }
  }

  subscribeToStream(streamId) {
    this.emit('subscribe_stream', { streamId });
  }

  unsubscribeFromStream(streamId) {
    this.emit('unsubscribe_stream', { streamId });
  }

  requestActionConfirmation(actionId, confirm) {
    this.emit('action_confirmation', { actionId, confirm });
  }

  isConnected() {
    return this.connected;
  }
}

export const wsService = new WebSocketService();