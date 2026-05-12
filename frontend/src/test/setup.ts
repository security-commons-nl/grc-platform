/**
 * Vitest setup — globaal geladen vóór elke test-file.
 *
 * - jest-dom matchers (`toBeInTheDocument` etc.) registreren
 * - MSW-server starten zodat tests netwerk-calls onderscheppen
 * - DOM-state opruimen tussen tests
 */

import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { server } from './msw-server';

beforeAll(() => {
  // 'error' = onverwachte requests laten falen — voorkomt stille mocks-gaten.
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});
