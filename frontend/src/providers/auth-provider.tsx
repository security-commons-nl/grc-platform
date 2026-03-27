'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import { getUser, setToken, clearToken } from '@/lib/auth';
import { api } from '@/lib/api-client';
import type { CurrentUser } from '@/lib/api-types';

interface AuthContextType {
  user: CurrentUser | null;
  isLoading: boolean;
  login: (
    userId: string,
    tenantId: string,
    role: string,
    domain?: string,
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const u = getUser();
    setUser(u);
    setIsLoading(false);
  }, []);

  const login = useCallback(
    async (userId: string, tenantId: string, role: string, domain?: string) => {
      const res = await api.auth.devToken({
        user_id: userId,
        tenant_id: tenantId,
        role,
        domain,
      });
      setToken(res.access_token);
      setUser(getUser());
    },
    [],
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    if (typeof window !== 'undefined') window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
