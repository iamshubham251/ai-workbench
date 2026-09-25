import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import { login as loginService, register as registerService, logout as logoutService } from "../services/authService";
interface AuthContextType {
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    // Check local storage for initial state
    const token = localStorage.getItem('auth_token');
    setIsAuthenticated(!!token);

    // Listen for unauthorized events emitted by apiClient
    const handleUnauthorized = () => setIsAuthenticated(false);
    window.addEventListener('auth:unauthorized', handleUnauthorized);

    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, []);

  const login = async (email: string, password: string) => {
    const data = await loginService(email, password);
    localStorage.setItem('auth_token', data.access_token);
    setIsAuthenticated(true);
  };

  const register = async (email: string, password: string) => {
    await registerService(email, password);
    // Automatically log in after registration
    await login(email, password);
  };

  const logout = () => {
    logoutService();
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
