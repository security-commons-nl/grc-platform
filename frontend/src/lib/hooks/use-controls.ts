import { useApi } from './use-api';
import type { ControlResponse } from '@/lib/api-types';

export function useControls() {
  return useApi<ControlResponse[]>('/controls/', '/controls/');
}
