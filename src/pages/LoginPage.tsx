import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Eye, EyeOff, LogIn, User, Lock, Mail, UserPlus } from 'lucide-react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { useAuth } from '@/contexts/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, register, isLoading, error } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState<string>('');

  const validateForm = () => {
    const errors: Record<string, string> = {};
    
    if (isRegisterMode) {
      if (!username.trim()) {
        errors.username = 'Username is required';
      } else if (username.length < 3) {
        errors.username = 'Username must be at least 3 characters';
      }
      
      if (!email.trim()) {
        errors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        errors.email = 'Please enter a valid email address';
      }
      
      if (!password) {
        errors.password = 'Password is required';
      } else if (password.length < 6) {
        errors.password = 'Password must be at least 6 characters';
      }
      
      if (!confirmPassword) {
        errors.confirmPassword = 'Please confirm your password';
      } else if (password !== confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
    } else {
      if (!username.trim()) {
        errors.username = 'Username is required';
      }
      
      if (!password) {
        errors.password = 'Password is required';
      }
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      // Error is handled by the useAuth hook
      console.error('Login failed:', err);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await register(username, email, password);
      navigate('/');
    } catch (err) {
      // Error is handled by the useAuth hook
      console.error('Registration failed:', err);
      
      // Error is handled by the useAuth hook and displayed above
    }
  };


  const clearErrors = () => {
    setValidationErrors({});
    setSuccessMessage('');
    // Note: We can't directly clear the error from useAuth here,
    // but it will be cleared when a new request is made
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    clearErrors();
    setUsername('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md">
          <Card className="border-border shadow-card">
            <CardHeader className="text-center space-y-4">
              <div className="mx-auto w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                {isRegisterMode ? (
                  <UserPlus className="w-8 h-8 text-primary-foreground" />
                ) : (
                  <LogIn className="w-8 h-8 text-primary-foreground" />
                )}
              </div>
              <div>
                <CardTitle className="text-2xl font-bold text-foreground">
                  {isRegisterMode ? 'Create Account' : 'Welcome Back'}
                </CardTitle>
                <p className="text-muted-foreground mt-2">
                  {isRegisterMode 
                    ? 'Sign up to get started with your account' 
                    : 'Sign in to your account to continue'
                  }
                </p>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-6">
              <form onSubmit={isRegisterMode ? handleRegister : handleLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-sm font-medium text-foreground">
                    Username
                  </Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="username"
                      type="text"
                      placeholder="Enter your username"
                      value={username}
                      onChange={(e) => {
                        setUsername(e.target.value);
                        clearErrors();
                      }}
                      className="pl-10"
                      required
                      disabled={isLoading}
                    />
                  </div>
                  {validationErrors.username && (
                    <p className="text-sm text-red-500">{validationErrors.username}</p>
                  )}
                </div>

                {isRegisterMode && (
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-sm font-medium text-foreground">
                      Email
                    </Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="Enter your email"
                        value={email}
                        onChange={(e) => {
                          setEmail(e.target.value);
                          clearErrors();
                        }}
                        className="pl-10"
                        required={isRegisterMode}
                        disabled={isLoading}
                      />
                    </div>
                    {validationErrors.email && (
                      <p className="text-sm text-red-500">{validationErrors.email}</p>
                    )}
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-medium text-foreground">
                    Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        clearErrors();
                      }}
                      className="pl-10 pr-10"
                      required
                      disabled={isLoading}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                      disabled={isLoading}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <Eye className="h-4 w-4 text-muted-foreground" />
                      )}
                    </Button>
                  </div>
                  {validationErrors.password && (
                    <p className="text-sm text-red-500">{validationErrors.password}</p>
                  )}
                </div>

                {isRegisterMode && (
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword" className="text-sm font-medium text-foreground">
                      Confirm Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="confirmPassword"
                        type={showConfirmPassword ? "text" : "password"}
                        placeholder="Confirm your password"
                        value={confirmPassword}
                        onChange={(e) => {
                          setConfirmPassword(e.target.value);
                          clearErrors();
                        }}
                        className="pl-10 pr-10"
                        required={isRegisterMode}
                        disabled={isLoading}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        disabled={isLoading}
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                    {validationErrors.confirmPassword && (
                      <p className="text-sm text-red-500">{validationErrors.confirmPassword}</p>
                    )}
                  </div>
                )}

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>
                      {error.includes('Username already taken') ? (
                        <div className="space-y-2">
                          <p>{error}</p>
                          <p className="text-sm">Please choose a different username.</p>
                        </div>
                      ) : (
                        error
                      )}
                    </AlertDescription>
                  </Alert>
                )}

                {successMessage && (
                  <Alert className="border-green-200 bg-green-50 text-green-800">
                    <AlertDescription>{successMessage}</AlertDescription>
                  </Alert>
                )}

                <Button 
                  type="submit" 
                  className="w-full bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-opacity" 
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                      {isRegisterMode ? 'Creating account...' : 'Signing in...'}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      {isRegisterMode ? (
                        <>
                          <UserPlus className="w-4 h-4" />
                          Create Account
                        </>
                      ) : (
                        <>
                          <LogIn className="w-4 h-4" />
                          Sign In
                        </>
                      )}
                    </div>
                  )}
                </Button>
              </form>


              <div className="text-center space-y-2">
                <p className="text-sm text-muted-foreground">
                  {isRegisterMode ? 'Already have an account? ' : "Don't have an account? "}
                  <Button 
                    variant="link" 
                    className="p-0 h-auto text-primary"
                    onClick={toggleMode}
                    disabled={isLoading}
                  >
                    {isRegisterMode ? 'Sign in' : 'Sign up'}
                  </Button>
                </p>
                <Button 
                  variant="ghost" 
                  onClick={() => navigate('/')}
                  className="text-sm text-muted-foreground hover:text-foreground"
                  disabled={isLoading}
                >
                  ← Back to Home
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default LoginPage;