import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '../types/auth';
import { authService } from '../services/auth.service';
import { getAccessToken } from '../services/api';

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, name: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      if (getAccessToken()) {
        try {
          const profile = await authService.getMe();
          setUser(profile);
        } catch {
          authService.logout();
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    loadUser();
  }, []);

  const login = async (email: string, pass: string) => {
    await authService.login(email, pass);
    const profile = await authService.getMe();
    setUser(profile);
  };

  const register = async (email: string, pass: string, name: string) => {
    await authService.register(email, pass, name);
    await login(email, pass);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const hasPermission = (permission: string) => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.permissions?.includes(permission) || false;
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, register, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth deve ser utilizado dentro de AuthProvider');
  return context;
};
