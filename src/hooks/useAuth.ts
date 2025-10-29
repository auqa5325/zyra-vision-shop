import { useState, useEffect, useCallback } from 'react';
import { authService, User, AuthState } from '@/services/authService';

export interface UseAuthReturn {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const useAuth = (): UseAuthReturn => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load stored auth state after component mounts
  useEffect(() => {
    const loadStoredAuth = () => {
      try {
        const storedToken = localStorage.getItem('accessToken');
        const storedUser = localStorage.getItem('user');
        
        if (storedToken && storedUser) {
          const user = JSON.parse(storedUser);
          setAuthState({
            isAuthenticated: true,
            user,
            token: storedToken,
          });
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
  }, []);

  // Update auth state when localStorage changes (e.g., from another tab)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'accessToken' || e.key === 'user') {
        const token = localStorage.getItem('accessToken');
        const user = localStorage.getItem('user');
        
        if (token && user) {
          try {
            setAuthState({
              isAuthenticated: true,
              user: JSON.parse(user),
              token,
            });
          } catch (error) {
            console.error('Failed to parse user data from storage event:', error);
            setAuthState({
              isAuthenticated: false,
              user: null,
              token: null,
            });
          }
        } else {
          setAuthState({
            isAuthenticated: false,
            user: null,
            token: null,
          });
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Check token validity on mount and periodically - simplified version
  useEffect(() => {
    if (!authState.isAuthenticated || !authState.token) {
      return;
    }

    const checkTokenValidity = async () => {
      try {
        const user = await authService.getCurrentUser(authState.token!);
        setAuthState(prev => ({
          ...prev,
          user,
        }));
      } catch (error) {
        console.error('Token validation failed:', error);
        // Token is invalid, clear state
        setAuthState({
          isAuthenticated: false,
          user: null,
          token: null,
        });
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      }
    };

    // Add a small delay to ensure backend is ready
    const timeoutId = setTimeout(checkTokenValidity, 1000);
    
    // Set up periodic token validation (every 5 minutes)
    const interval = setInterval(checkTokenValidity, 5 * 60 * 1000);
    
    return () => {
      clearTimeout(timeoutId);
      clearInterval(interval);
    };
  }, [authState.isAuthenticated, authState.token]);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authService.login({ username, password });
      
      // Get user info
      const user = await authService.getCurrentUser(response.access_token);
      
      // Update state
      setAuthState({
        isAuthenticated: true,
        user,
        token: response.access_token,
      });
      
      // Save to localStorage
      localStorage.setItem('accessToken', response.access_token);
      localStorage.setItem('refreshToken', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(user));
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear state and storage regardless of API call success
      setAuthState({
        isAuthenticated: false,
        user: null,
        token: null,
      });
      
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      
      setIsLoading(false);
    }
  }, []);

  return {
    isAuthenticated: authState.isAuthenticated,
    user: authState.user,
    token: authState.token,
    login,
    logout,
    isLoading,
    error,
  };
};