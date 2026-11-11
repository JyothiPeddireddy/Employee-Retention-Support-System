import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user_info');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(() => localStorage.getItem('access_token') || null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize and verify session on initial mount
  useEffect(() => {
    const verifySession = async () => {
      const savedToken = localStorage.getItem('access_token');
      if (!savedToken) {
        setLoading(false);
        return;
      }

      try {
        const profile = await authApi.getMe();
        setUser(profile);
        localStorage.setItem('user_info', JSON.stringify(profile));
      } catch (err) {
        console.warn('Session verification failed:', err.message);
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        setUser(null);
        setToken(null);
      } finally {
        setLoading(false);
      }
    };

    verifySession();
  }, []);

  const login = async (username, password) => {
    setError(null);
    try {
      const data = await authApi.login(username, password);
      // data: TokenResponse { access_token, token_type, expires_in_minutes, user_id, username, role, employee_id }
      const tokenVal = data.access_token;
      const userObj = {
        user_id: data.user_id,
        username: data.username,
        role: data.role,
        employee_id: data.employee_id,
      };

      localStorage.setItem('access_token', tokenVal);
      localStorage.setItem('user_info', JSON.stringify(userObj));
      setToken(tokenVal);
      setUser(userObj);
      return userObj;
    } catch (err) {
      setError(err.message || 'Login failed.');
      throw err;
    }
  };

  const register = async (userData) => {
    setError(null);
    try {
      const createdUser = await authApi.register(userData);
      // Automatically log in after registration
      return await login(userData.username, userData.password);
    } catch (err) {
      setError(err.message || 'Registration failed.');
      throw err;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      setUser(null);
      setToken(null);
    }
  };

  const changePassword = async (currentPassword, newPassword) => {
    return await authApi.changePassword(currentPassword, newPassword);
  };

  const hasRole = useCallback(
    (...allowedRoles) => {
      if (!user || !user.role) return false;
      const flatRoles = allowedRoles.flat();
      return flatRoles.includes(user.role);
    },
    [user]
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role: user?.role || null,
        isAuthenticated: !!token && !!user,
        loading,
        error,
        login,
        register,
        logout,
        changePassword,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
