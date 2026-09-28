import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiRequest, setToken, removeToken, getToken } from '../api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const token = getToken();
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const profile = await apiRequest('/auth/me');
        setUser(profile);
      } catch (err) {
        console.error("Auth session check failed:", err);
        removeToken();
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, []);

  const login = async (username, password) => {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: { username, password }
    });
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    removeToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
