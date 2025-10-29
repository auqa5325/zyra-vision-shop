/**
 * Base API configuration and utilities
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8005';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    // Get auth token from localStorage
    const accessToken = localStorage.getItem('accessToken');
    
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    // Add Authorization header if token exists
    if (accessToken) {
      defaultHeaders['Authorization'] = `Bearer ${accessToken}`;
    }

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      // Add timeout to prevent hanging requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await fetch(url, {
        ...config,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
      }

      // Handle 204 No Content responses
      if (response.status === 204) {
        return {} as T;
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return {} as T;
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('API request failed: Request timeout');
        }
        throw new Error(`API request failed: ${error.message}`);
      }
      // Handle non-Error objects
      const errorMessage = typeof error === 'object' && error !== null 
        ? JSON.stringify(error) 
        : String(error);
      throw new Error(`API request failed: ${errorMessage}`);
    }
  }

  async get<T>(endpoint: string, params?: Record<string, any> | { params?: Record<string, any> }, options?: RequestInit): Promise<T> {
    const url = new URL(`${this.baseURL}${endpoint}`);
    
    // Handle both direct params and axios-style { params: {...} }
    const actualParams = params && 'params' in params ? params.params : params;
    
    if (actualParams) {
      Object.entries(actualParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    return this.request<T>(url.pathname + url.search, options);
  }

  async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
  }

  async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
  }

  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
      ...options,
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);

export default apiClient;
