/**
 * Centrale MSW-handler-lijst.
 *
 * Hier staan default-mocks die de meeste tests genoeg vinden. Test-specifieke
 * mocks override je inline via `server.use(...)` binnen een test — die zijn
 * automatisch weer weg na `afterEach` reset.
 */

import { http, HttpResponse } from 'msw';

const API = 'http://localhost:8000/api/v1';

export const handlers = [
  // Auth: huidige user — default 'admin'
  http.get(`${API}/auth/me`, () =>
    HttpResponse.json({
      id: '11111111-1111-1111-1111-111111111111',
      tenant_id: '22222222-2222-2222-2222-222222222222',
      role: 'admin',
      domain: null,
      token_type: 'user',
      agent_name: null,
    }),
  ),

  // Risks list — leeg by default
  http.get(`${API}/risks/`, () => HttpResponse.json([])),

  // AI-systems list — leeg by default
  http.get(`${API}/ai-systems/`, () => HttpResponse.json([])),

  // Classifier-advies — deterministische dummy
  http.post(`${API}/ai-systems/classify-suggestion`, () =>
    HttpResponse.json({
      suggested_risk: 'limited',
      reasoning: 'Test-reasoning (MSW mock).',
      triggered_by: ['mock-keyword'],
    }),
  ),
];
