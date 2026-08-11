import React, { createContext, useContext, useState } from 'react';

interface AuthContextType {
  user: any;
  login: (userData: any, token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any>(() => {
    try {
      const savedUser = localStorage.getItem('user');
      if (savedUser) return JSON.parse(savedUser);

      const token = localStorage.getItem('token');
      if (token) {
        const parts = token.split('.');
        if (parts.length === 3) {
          const payload = JSON.parse(window.atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
          return {
            email: payload.sub || 'User',
            user_id: payload.user_id || 1,
            merchant_id: payload.merchant_id || 1,
          };
        }
      }
    } catch (e) {
      console.warn("Auth initialization error:", e);
    }
    return null;
  });

  const login = (userData: any, token: string) => {
    const validUser = {
      email: userData?.email || 'User',
      user_id: userData?.user_id || 1,
      merchant_id: userData?.merchant_id || 1,
    };
    setUser(validUser);
    localStorage.setItem('user', JSON.stringify(validUser));
    localStorage.setItem('token', token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
