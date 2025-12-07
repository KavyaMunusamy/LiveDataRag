import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

// Initialize the application
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Service worker registration (for PWA)
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js').then(
      (registration) => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      },
      (err) => {
        console.log('ServiceWorker registration failed: ', err);
      }
    );
  });
}

// Error boundary for initialization errors
window.addEventListener('error', (event) => {
  console.error('Application error:', event.error);
  
  // You can send errors to your error tracking service here
  if (process.env.NODE_ENV === 'production') {
    // Example: send to Sentry, LogRocket, etc.
  }
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  event.preventDefault();
});

// Performance monitoring
if (process.env.NODE_ENV === 'production') {
  // Initialize performance monitoring tools
  // Example: Google Analytics, Hotjar, etc.
}

// Debug helpers
if (process.env.NODE_ENV === 'development') {
  // Expose useful variables for debugging
  window.__APP_VERSION__ = process.env.REACT_APP_VERSION || '1.0.0';
  window.__BUILD_DATE__ = process.env.REACT_APP_BUILD_DATE || new Date().toISOString();
}