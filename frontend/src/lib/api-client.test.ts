/**
 * Integration-style tests voor api-client tegen MSW.
 *
 * Test bevat een mini auth-shim: api-client roept getToken() vanuit
 * localStorage. We vullen die in beforeEach zodat alle requests geldig zijn.
 */

import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { http, HttpResponse } from 'msw';
import { api, ApiError } from './api-client';
import { setToken, clearToken } from './auth';
import { server } from '@/test/msw-server';

const API = 'http://localhost:8000/api/v1';

beforeEach(() => {
  // Geldige JWT-vorm vereist 3 base64-segmenten; voor MSW-tests is de inhoud
  // niet belangrijk omdat de server-side check er niet is. Maar `decodeJwt`
  // in lib/auth zou kunnen klagen — we vermijden die path door alleen
  // localStorage te setten met een token-string.
  setToken('header.payload.signature');
});

afterEach(() => {
  clearToken();
});

describe('api-client', () => {
  it('aiSystems.list bouwt query-string op uit filters', async () => {
    let capturedUrl: string | null = null;
    server.use(
      http.get(`${API}/ai-systems/`, ({ request }) => {
        capturedUrl = request.url;
        return HttpResponse.json([]);
      }),
    );

    await api.aiSystems.list({
      eu_ai_act_risk: 'high',
      deployment_status: 'deployed',
    });

    expect(capturedUrl).toContain('eu_ai_act_risk=high');
    expect(capturedUrl).toContain('deployment_status=deployed');
  });

  it('aiSystems.list zonder filters stuurt geen query-string', async () => {
    let capturedUrl: string | null = null;
    server.use(
      http.get(`${API}/ai-systems/`, ({ request }) => {
        capturedUrl = request.url;
        return HttpResponse.json([]);
      }),
    );

    await api.aiSystems.list();

    expect(capturedUrl).not.toContain('?');
  });

  it('gooit ApiError met status + body bij 4xx', async () => {
    server.use(
      http.get(`${API}/risks/abc`, () =>
        HttpResponse.json({ detail: 'Risico niet gevonden' }, { status: 404 }),
      ),
    );

    let caught: unknown = null;
    try {
      await api.risks.get('abc');
    } catch (err) {
      caught = err;
    }

    expect(caught).toBeInstanceOf(ApiError);
    if (caught instanceof ApiError) {
      expect(caught.status).toBe(404);
      expect(caught.body).toEqual({ detail: 'Risico niet gevonden' });
    }
  });

  it('risks.simulate stuurt include_samples=true wanneer gevraagd', async () => {
    let capturedUrl: string | null = null;
    server.use(
      http.post(`${API}/risks/r-1/simulate`, ({ request }) => {
        capturedUrl = request.url;
        return HttpResponse.json({
          risk_id: 'r-1',
          distribution: 'uniform',
          parameters: {},
          iterations: 10000,
          statistics: { mean: 0, std: 0, min: 0, max: 0 },
          percentiles: { p5: 0, p25: 0, p50: 0, p75: 0, p95: 0, p99: 0 },
          expected_loss: 0,
          var_95: 0,
          var_99: 0,
        });
      }),
    );

    await api.risks.simulate('r-1', { iterations: 5000, includeSamples: true, seed: 42 });

    expect(capturedUrl).toContain('iterations=5000');
    expect(capturedUrl).toContain('seed=42');
    expect(capturedUrl).toContain('include_samples=true');
  });
});
