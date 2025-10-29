// Utility functions for authentication state management

export const getStoredAuthState = () => {
  try {
    const token = localStorage.getItem('accessToken');
    const user = localStorage.getItem('user');
    const refreshToken = localStorage.getItem('refreshToken');
    
    return {
      token,
      user: user ? JSON.parse(user) : null,
      refreshToken,
      isAuthenticated: !!(token && user),
    };
  } catch (error) {
    console.error('Failed to parse stored auth state:', error);
    return {
      token: null,
      user: null,
      refreshToken: null,
      isAuthenticated: false,
    };
  }
};

export const clearStoredAuthState = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
};

export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    console.error('Failed to parse token:', error);
    return true;
  }
};

// Debug function to log current auth state
export const debugAuthState = () => {
  const authState = getStoredAuthState();
    isAuthenticated: authState.isAuthenticated,
    username: authState.user?.username,
    email: authState.user?.email,
    tokenExpired: authState.token ? isTokenExpired(authState.token) : 'No token',
    hasRefreshToken: !!authState.refreshToken,
  });
  return authState;
};

