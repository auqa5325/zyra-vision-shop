/**
 * Authentication service for connecting to backend
 */

import apiClient from './api';

export interface User {
  user_id: string;
  username?: string;
  email?: string;
  profile?: Record<string, any>;
  is_anonymous: boolean;
  created_at: string;
  last_seen_at?: string;
  is_active: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username?: string;
  email?: string;
  password?: string;
  profile?: Record<string, any>;
  is_anonymous?: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}

class AuthService {
  private static instance: AuthService;
  private authState: AuthState = {
    isAuthenticated: false,
    user: null,
    token: null,
  };

  private constructor() {
    this.loadAuthFromStorage();
  }

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  /**
   * Load authentication state from localStorage
   */
  private loadAuthFromStorage(): void {
    const token = localStorage.getItem('accessToken');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      this.authState = {
        isAuthenticated: true,
        user: JSON.parse(user),
        token,
      };
    }
  }

  /**
   * Save authentication state to localStorage
   */
  private saveAuthToStorage(token: string, user: User, refreshToken?: string): void {
    localStorage.setItem('accessToken', token);
    localStorage.setItem('user', JSON.stringify(user));
    if (refreshToken) {
      localStorage.setItem('refreshToken', refreshToken);
    }
  }

  /**
   * Clear authentication state from localStorage
   */
  private clearAuthFromStorage(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }

  /**
   * Register a new user
   */
  async register(userData: RegisterRequest): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>('/api/auth/register', userData);
      
      // Get user info
      const userResponse = await this.getCurrentUser(response.access_token);
      
      // Ensure username is set (fallback to profile.username if needed)
      if (!userResponse.username && userResponse.profile?.username) {
        userResponse.username = userResponse.profile.username;
      }
      
      // Save to state and storage
      this.authState = {
        isAuthenticated: true,
        user: userResponse,
        token: response.access_token,
      };
      
      this.saveAuthToStorage(response.access_token, userResponse, response.refresh_token);
      
      return response;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  /**
   * Login user
   */
  async login(loginData: LoginRequest): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>('/api/auth/login', loginData);
      
      // Get user info
      const userResponse = await this.getCurrentUser(response.access_token);
      
      // Extract session info from token (if available)
      const tokenPayload = this.parseJWT(response.access_token);
      const sessionId = tokenPayload?.session_id;
      
      // Console log for frontend verification
      console.log('🔐 [FRONTEND_LOGIN] Session created:', {
        sessionId: sessionId || 'Not available in token',
        userId: userResponse.user_id,
        username: userResponse.username,
        loginTime: new Date().toISOString(),
        tokenExpiry: tokenPayload?.exp ? new Date(tokenPayload.exp * 1000).toISOString() : 'Unknown'
      });
      
      // Save to state and storage
      this.authState = {
        isAuthenticated: true,
        user: userResponse,
        token: response.access_token,
      };
      
      this.saveAuthToStorage(response.access_token, userResponse, response.refresh_token);
      
      return response;
    } catch (error) {
      console.error('❌ [AUTH] Login failed:', error);
      throw error;
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(token?: string): Promise<User> {
    try {
      const response = await apiClient.get<User>('/api/auth/me', undefined, {
        headers: {
          'Authorization': `Bearer ${token || this.authState.token}`
        }
      });
      return response;
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw error;
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<TokenResponse> {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post<TokenResponse>('/api/auth/refresh', {
        refresh_token: refreshToken
      });

      // Update token in state and storage
      this.authState.token = response.access_token;
      localStorage.setItem('accessToken', response.access_token);

      return response;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.logout();
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      // Extract session info before logout
      const tokenPayload = this.parseJWT(this.authState.token || '');
      const sessionId = tokenPayload?.session_id;
      const userId = tokenPayload?.user_id || tokenPayload?.sub;
      
      // Console log for frontend verification
      console.log('🚪 [FRONTEND_LOGOUT] Session ending:', {
        sessionId: sessionId || 'Not available in token',
        userId: userId,
        logoutTime: new Date().toISOString(),
        sessionDuration: 'Calculated on server'
      });
      
      // Call logout endpoint if authenticated
      if (this.authState.isAuthenticated) {
        const logoutResponse = await apiClient.post('/api/auth/logout');
        
        // Console log for logout completion
        console.log('✅ [FRONTEND_LOGOUT] Logout completed:', {
          sessionId: sessionId || 'Not available in token',
          userId: userId,
          logoutResponse: logoutResponse
        });
      }
    } catch (error) {
      console.error('❌ [AUTH] Logout request failed:', error);
    } finally {
      // Clear state regardless of API call success
      this.authState = {
        isAuthenticated: false,
        user: null,
        token: null,
      };
      this.clearAuthFromStorage();
      
      // Clear user-specific data from localStorage
      this.clearUserData();
    }
  }

  /**
   * Parse JWT token to extract payload
   */
  private parseJWT(token: string): any {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.warn('Failed to parse JWT token:', error);
      return null;
    }
  }

  /**
   * Clear user-specific data from localStorage
   */
  private clearUserData(): void {
    // Clear cart data
    localStorage.removeItem('cart');
    
    // Clear wishlist data
    localStorage.removeItem('wishlist');
    
    // Clear any other user-specific data
    localStorage.removeItem('userPreferences');
    localStorage.removeItem('recentSearches');
    
    // Dispatch events to notify components
    window.dispatchEvent(new CustomEvent('userLoggedOut'));
    window.dispatchEvent(new CustomEvent('cartUpdated'));
    window.dispatchEvent(new CustomEvent('wishlistUpdated'));
  }

  /**
   * Get current authentication state
   */
  getAuthState(): AuthState {
    return { ...this.authState };
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.authState.isAuthenticated;
  }

  /**
   * Get current user
   */
  getCurrentUserSync(): User | null {
    return this.authState.user;
  }

  /**
   * Get current token
   */
  getToken(): string | null {
    return this.authState.token;
  }
}

export const authService = AuthService.getInstance();
export default authService;
