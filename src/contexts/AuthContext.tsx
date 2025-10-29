import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { authService, User } from '@/services/authService';

// Extend Window interface for development warning flag
declare global {
  interface Window {
    __authContextWarningShown?: boolean;
  }
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    isLoading: false,
    error: null,
  });
  const [isInitialized, setIsInitialized] = useState(false);

  // Load stored auth state after component mounts
  useEffect(() => {
    const loadStoredAuth = () => {
      try {
        const storedToken = localStorage.getItem('accessToken');
        const storedUser = localStorage.getItem('user');
        
        if (storedToken && storedUser) {
          const user = JSON.parse(storedUser);
          setAuthState(prev => ({
            ...prev,
            isAuthenticated: true,
            user,
            token: storedToken,
          }));
        }
      } catch (error) {
        console.error('Failed to load stored auth state:', error);
        // Clear invalid data
        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
        localStorage.removeItem('refreshToken');
      }
    };

    loadStoredAuth();
    setIsInitialized(true);
  }, []);

  // Update auth state when localStorage changes (e.g., from another tab)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'accessToken' || e.key === 'user') {
        const token = localStorage.getItem('accessToken');
        const user = localStorage.getItem('user');
        
        if (token && user) {
          try {
            setAuthState(prev => ({
              ...prev,
              isAuthenticated: true,
              user: JSON.parse(user),
              token,
            }));
          } catch (error) {
            console.error('Failed to parse user data from storage event:', error);
            setAuthState(prev => ({
              ...prev,
              isAuthenticated: false,
              user: null,
              token: null,
            }));
          }
        } else {
          setAuthState(prev => ({
            ...prev,
            isAuthenticated: false,
            user: null,
            token: null,
          }));
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await authService.login({ username, password });
      
      // Get user info from authService (it already calls getCurrentUser)
      const user = authService.getCurrentUserSync();
      
      // Update state
      setAuthState({
        isAuthenticated: true,
        user,
        token: response.access_token,
        isLoading: false,
        error: null,
      });
      
      // Save to localStorage (authService already saves, but ensure consistency)
      localStorage.setItem('accessToken', response.access_token);
      localStorage.setItem('refreshToken', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      console.error('❌ [AUTH CONTEXT] Login failed:', errorMessage);
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  const register = useCallback(async (username: string, email: string, password: string) => {
    setAuthState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await authService.register({
        username,
        email,
        password,
        profile: { username },
        is_anonymous: false
      });
      
      // Get user info from authService (it already calls getCurrentUser)
      const user = authService.getCurrentUserSync();
      
      // Update state
      setAuthState({
        isAuthenticated: true,
        user,
        token: response.access_token,
        isLoading: false,
        error: null,
      });
      
      // Save to localStorage (authService already saves, but ensure consistency)
      localStorage.setItem('accessToken', response.access_token);
      localStorage.setItem('refreshToken', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed';
      console.error('❌ [AUTH CONTEXT] Registration failed:', errorMessage);
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw err;
    }
  }, []);

  const logout = useCallback(async () => {
    setAuthState(prev => ({ ...prev, isLoading: true }));
    
    try {
      await authService.logout();
    } catch (error) {
      console.error('❌ [AUTH CONTEXT] Logout error:', error);
    } finally {
      // Clear state and storage regardless of API call success
      setAuthState({
        isAuthenticated: false,
        user: null,
        token: null,
        isLoading: false,
        error: null,
      });
      
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    }
  }, []);

  const value: AuthContextType = {
    ...authState,
    login,
    register,
    logout,
  };

  // Don't render children until context is initialized
  if (!isInitialized) {
    return null;
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    // During development/hot reload, sometimes context is undefined temporarily
    // Return a default context to prevent crashes
    if (process.env.NODE_ENV === 'development') {
      // Only warn once per session to avoid spam during hot reloads
      if (!window.__authContextWarningShown) {
        console.warn('useAuth called outside AuthProvider, returning default context. This may happen during hot reloads.');
        window.__authContextWarningShown = true;
      }
      return {
        isAuthenticated: false,
        user: null,
        token: null,
        isLoading: false,
        error: null,
        login: async () => {},
        register: async () => {},
        logout: async () => {}
      };
    }
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

