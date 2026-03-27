import { useApi } from './use-api';
import type { RiskResponse } from '@/lib/api-types';

export function useRisks() {
  return useApi<RiskResponse[]>('/risks/', '/risks/');
}
