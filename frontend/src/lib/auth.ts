import { decodeJwt } from 'jose';
import type { CurrentUser } from './api-types';

const TOKEN_KEY = 'ims_token';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function getUser(): CurrentUser | null {
  const token = getToken();
  if (!token) return null;
  try {
    const claims = decodeJwt(token);
    if (claims.exp && claims.exp * 1000 < Date.now()) {
      clearToken();
      return null;
    }
    return {
      id: claims.sub as string,
      tenant_id: claims.tenant_id as string,
      role: claims.role as string,
      domain: (claims.domain as string) || null,
      token_type: (claims.token_type as string) || 'user',
      agent_name: (claims.agent_name as string) || null,
    };
  } catch {
    clearToken();
    return null;
  }
}

export function isAuthenticated(): boolean {
  return getUser() !== null;
}
