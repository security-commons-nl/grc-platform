import useSWR from 'swr';
import { apiFetch } from '@/lib/api-client';

export function useApi<T>(key: string | null, path?: string) {
  const { data, error, isLoading, mutate } = useSWR<T>(key, () => apiFetch<T>(path || key!));
  return { data, error, isLoading, mutate };
}
