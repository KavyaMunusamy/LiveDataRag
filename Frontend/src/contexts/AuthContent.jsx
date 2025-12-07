import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        // Check for existing session
        const token = localStorage.getItem('access_token');
        if (token) {
            validateToken(token);
        } else {
            setLoading(false);
        }
    }, []);

    const validateToken = async (token) => {
        try {
            // Validate token with backend
            // This is a placeholder - implement actual validation
            const userData = JSON.parse(localStorage.getItem('user_data') || 'null');
            if (userData) {
                setUser(userData);
            }
        } catch (err) {
            console.error('Token validation failed:', err);
            logout();
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            setError(null);
            setLoading(true);
            
            // Mock login - replace with actual API call
            const mockUser = {
                id: 'user_123',
                email,
                name: 'Demo User',
                role: 'admin',
                permissions: ['read', 'write', 'execute'],
                avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(email)}&background=1976d2&color=fff`
            };
            
            const mockToken = 'mock_jwt_token';
            
            // Store in localStorage
            localStorage.setItem('access_token', mockToken);
            localStorage.setItem('user_data', JSON.stringify(mockUser));
            
            setUser(mockUser);
            navigate('/dashboard');
            
            return { success: true };
        } catch (err) {
            setError(err.message || 'Login failed');
            return { success: false, error: err.message };
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('refresh_token');
        setUser(null);
        navigate('/login');
    };

    const register = async (userData) => {
        try {
            setError(null);
            setLoading(true);
            
            // Mock registration - replace with actual API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Auto-login after registration
            return await login(userData.email, userData.password);
        } catch (err) {
            setError(err.message || 'Registration failed');
            return { success: false, error: err.message };
        } finally {
            setLoading(false);
        }
    };

    const updateProfile = async (updates) => {
        try {
            setError(null);
            
            // Mock update - replace with actual API call
            const updatedUser = { ...user, ...updates };
            localStorage.setItem('user_data', JSON.stringify(updatedUser));
            setUser(updatedUser);
            
            return { success: true };
        } catch (err) {
            setError(err.message || 'Update failed');
            return { success: false, error: err.message };
        }
    };

    const changePassword = async (oldPassword, newPassword) => {
        try {
            setError(null);
            setLoading(true);
            
            // Mock password change - replace with actual API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            return { success: true };
        } catch (err) {
            setError(err.message || 'Password change failed');
            return { success: false, error: err.message };
        } finally {
            setLoading(false);
        }
    };

    const hasPermission = (permission) => {
        if (!user) return false;
        return user.permissions?.includes(permission) || user.role === 'admin';
    };

    const value = {
        user,
        loading,
        error,
        login,
        logout,
        register,
        updateProfile,
        changePassword,
        hasPermission,
        isAuthenticated: !!user
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

// Protected route component
export const ProtectedRoute = ({ children, requiredPermissions = [] }) => {
    const { isAuthenticated, loading, hasPermission } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            navigate('/login', { replace: true });
        }
    }, [loading, isAuthenticated, navigate]);

    if (loading) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh' 
            }}>
                <div>Loading authentication...</div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return null;
    }

    // Check permissions
    const hasRequiredPermissions = requiredPermissions.every(permission => 
        hasPermission(permission)
    );

    if (requiredPermissions.length > 0 && !hasRequiredPermissions) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh',
                flexDirection: 'column',
                gap: '20px'
            }}>
                <h1>Access Denied</h1>
                <p>You don't have permission to access this page.</p>
                <button onClick={() => navigate('/dashboard')}>
                    Go to Dashboard
                </button>
            </div>
        );
    }

    return children;
};