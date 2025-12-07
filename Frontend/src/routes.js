import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Lazy load components for better performance
const Dashboard = lazy(() => import('./components/Dashboard/Dashboard'));
const QueryInterface = lazy(() => import('./components/QueryInterface/QueryInterface'));
const RulesManager = lazy(() => import('./components/RulesManager/RulesManager'));
const Settings = lazy(() => import('./components/Settings/Settings'));
const Login = lazy(() => import('./components/Auth/Login'));
const Register = lazy(() => import('./components/Auth/Register'));

// Layout components
const Layout = lazy(() => import('./components/Layout'));
const Sidebar = lazy(() => import('./components/Layout/Sidebar'));
const Header = lazy(() => import('./components/Layout/Header'));

// Error pages
const NotFound = lazy(() => import('./components/Errors/NotFound'));
const Unauthorized = lazy(() => import('./components/Errors/Unauthorized'));

// Loading fallback component
const LoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh' 
  }}>
    <LoadingSpinner 
      message="Loading application..." 
      fullScreen 
    />
  </div>
);

// Main routes configuration
export const AppRoutes = () => {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        
        {/* Protected routes with layout */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="query" element={<QueryInterface />} />
          <Route path="rules" element={<RulesManager />} />
          <Route path="settings" element={<Settings />} />
          
          {/* Nested routes for settings */}
          <Route path="settings/profile" element={<Settings tab="profile" />} />
          <Route path="settings/security" element={<Settings tab="security" />} />
          <Route path="settings/notifications" element={<Settings tab="notifications" />} />
          <Route path="settings/api" element={<Settings tab="api" />} />
        </Route>
        
        {/* Error routes */}
        <Route path="/404" element={<NotFound />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </Suspense>
  );
};

// Protected route wrapper
const ProtectedRoute = ({ children, requiredPermissions = [] }) => {
  const { isAuthenticated, loading, hasPermission } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingFallback />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check permissions if required
  if (requiredPermissions.length > 0) {
    const hasRequiredPermissions = requiredPermissions.every(permission => 
      hasPermission(permission)
    );
    
    if (!hasRequiredPermissions) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return children;
};

// Route configuration for navigation
export const navigationRoutes = [
  {
    path: '/dashboard',
    label: 'Dashboard',
    icon: 'dashboard',
    description: 'System overview and monitoring',
    permissions: ['read']
  },
  {
    path: '/query',
    label: 'Query Interface',
    icon: 'search',
    description: 'Ask questions and analyze data',
    permissions: ['read', 'execute']
  },
  {
    path: '/rules',
    label: 'Rules Manager',
    icon: 'rule',
    description: 'Create and manage automation rules',
    permissions: ['read', 'write']
  },
  {
    path: '/settings',
    label: 'Settings',
    icon: 'settings',
    description: 'System configuration',
    permissions: ['admin']
  }
];

// Settings sub-routes
export const settingsRoutes = [
  {
    path: '/settings/profile',
    label: 'Profile',
    icon: 'person',
    description: 'Manage your account profile'
  },
  {
    path: '/settings/security',
    label: 'Security',
    icon: 'security',
    description: 'Password and security settings'
  },
  {
    path: '/settings/notifications',
    label: 'Notifications',
    icon: 'notifications',
    description: 'Configure notification preferences'
  },
  {
    path: '/settings/api',
    label: 'API Settings',
    icon: 'api',
    description: 'API keys and integration settings'
  }
];

// Export route utilities
export const getRouteConfig = (path) => {
  const allRoutes = [...navigationRoutes, ...settingsRoutes];
  return allRoutes.find(route => route.path === path);
};

export const isActiveRoute = (currentPath, routePath) => {
  if (routePath === '/') {
    return currentPath === '/';
  }
  return currentPath.startsWith(routePath);
};