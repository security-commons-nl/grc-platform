/**
 * MSW-server voor Node (Vitest-omgeving).
 *
 * Browsers gebruiken `setupWorker` met een service worker; in tests draaien
 * we onder Node en gebruiken `setupServer`. De handler-lijst is gedeeld
 * tussen omgevingen via `msw-handlers.ts`.
 */

import { setupServer } from 'msw/node';
import { handlers } from './msw-handlers';

export const server = setupServer(...handlers);
