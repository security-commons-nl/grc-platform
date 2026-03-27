import { getToken, clearToken } from './auth';
import { API_BASE_URL } from './constants';
import type { TokenResponse, DevTokenRequest, CurrentUser } from './api-types';

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
  ) {
    super(`API Error ${status}`);
  }
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });

  if (res.status === 401) {
    clearToken();
    if (typeof window !== 'undefined') window.location.href = '/login';
    throw new ApiError(401, 'Unauthorized');
  }

  if (!res.ok) {
    throw new ApiError(res.status, await res.json().catch(() => null));
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  auth: {
    devToken: (data: DevTokenRequest) =>
      apiFetch<TokenResponse>('/auth/dev-token', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    me: () => apiFetch<CurrentUser>('/auth/me'),
  },
};

export { apiFetch };
