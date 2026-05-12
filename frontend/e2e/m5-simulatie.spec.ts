import { test, expect, type Page, type APIRequestContext } from '@playwright/test';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

async function getDevToken(request: APIRequestContext): Promise<string> {
  const r = await request.post(`${API_BASE}/api/v1/auth/dev-token`, {
    data: {
      user_id: '00000000-0000-0000-0000-000000000001',
      tenant_id: '00000000-0000-0000-0000-000000000001',
      role: 'admin',
    },
  });
  expect(r.ok()).toBeTruthy();
  const body = await r.json();
  return body.access_token;
}

async function createScope(
  request: APIRequestContext,
  token: string,
  name: string,
): Promise<string> {
  const r = await request.post(`${API_BASE}/api/v1/scopes/`, {
    data: { name, type: 'cluster', domain: 'ISMS' },
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(r.status(), `scope creation failed: ${await r.text()}`).toBe(201);
  const body = await r.json();
  return body.id;
}

async function createRiskWithTriangular(
  request: APIRequestContext,
  token: string,
  scopeId: string,
  title: string,
): Promise<string> {
  const r = await request.post(`${API_BASE}/api/v1/risks/`, {
    data: {
      scope_id: scopeId,
      domain: 'ISMS',
      title,
      description: 'E2E-test risico met triangular distributie',
      likelihood: 3,
      impact: 4,
      financial_impact_eur: 25000,
      financial_impact_min_eur: 10000,
      financial_impact_max_eur: 100000,
      impact_distribution: 'triangular',
    },
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(r.status(), `risk creation failed: ${await r.text()}`).toBe(201);
  const body = await r.json();
  return body.id;
}

async function loginViaUI(page: Page) {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'Inloggen' }).click();
  await page.waitForURL(/\/inrichten/, { timeout: 15_000, waitUntil: 'domcontentloaded' });
}

test.describe('M5 — Monte Carlo simulatie', () => {
  test('simuleer triangular risico → histogram, percentielen en interpretatie verschijnen', async ({
    page,
    request,
  }) => {
    // Setup via API (sneller en deterministischer dan UI-formulier doorlopen)
    const token = await getDevToken(request);
    const scopeId = await createScope(request, token, `Scope-${Date.now()}`);
    const riskTitle = `Ransomware-incident ${Date.now()}`;
    await createRiskWithTriangular(request, token, scopeId, riskTitle);

    // Navigatie via UI
    await loginViaUI(page);
    await page.goto('/beheer/risicos');
    await page.waitForLoadState('networkidle');

    // Risico moet in tabel staan met Simuleer-knop
    const row = page.locator('tr', { hasText: riskTitle });
    await expect(row).toBeVisible({ timeout: 10_000 });
    const simulateBtn = row.getByRole('button', { name: 'Simuleer' });
    await expect(simulateBtn).toBeVisible();

    // Klik en wacht op resultaat-card
    await simulateBtn.click();

    // Monte Carlo-titel verschijnt — staat boven in de pagina (scrollTo top)
    await expect(page.getByText('Monte Carlo-simulatie')).toBeVisible({ timeout: 15_000 });

    // Histogram-sectie verschijnt
    await expect(page.getByText('Verdeling van schade-uitkomsten')).toBeVisible();
    await expect(page.getByText('10.000 simulaties')).toBeVisible();

    // Percentielen-samenvatting verschijnt
    await expect(page.getByText('Percentielen (samenvattend)')).toBeVisible();
    await expect(page.getByText('P95')).toBeVisible();
    await expect(page.getByText('P99')).toBeVisible();

    // Interpretation-blok verschijnt
    await expect(page.getByText('Interpretatie', { exact: false })).toBeVisible();
    await expect(
      page.getByText(/In 1 op de 20 gevallen .*5%.* loopt de schade op tot meer dan/),
    ).toBeVisible();
    await expect(
      page.getByText(/In 1 op de 100 gevallen .*1%.* loopt de schade op tot meer dan/),
    ).toBeVisible();
  });

  test('twee simulaties met dezelfde seed leveren identieke percentielen', async ({
    request,
  }) => {
    // Pure API-test (geen UI nodig): valideert backend-reproduceerbaarheid die
    // de UI-vergelijking-feature later op gaat leunen.
    const token = await getDevToken(request);
    const scopeId = await createScope(request, token, `Scope-Seed-${Date.now()}`);
    const riskId = await createRiskWithTriangular(
      request,
      token,
      scopeId,
      `Seed-risk-${Date.now()}`,
    );

    const callSimulate = async () => {
      const r = await request.post(
        `${API_BASE}/api/v1/risks/${riskId}/simulate?iterations=5000&seed=42`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      expect(r.status()).toBe(200);
      return r.json();
    };

    const a = await callSimulate();
    const b = await callSimulate();

    expect(a.var_95).toBeCloseTo(b.var_95, 5);
    expect(a.var_99).toBeCloseTo(b.var_99, 5);
    expect(a.expected_loss).toBeCloseTo(b.expected_loss, 5);
    expect(a.percentiles.p50).toBeCloseTo(b.percentiles.p50, 5);
  });

  test('simulatie-historie groeit met elke run', async ({ request }) => {
    const token = await getDevToken(request);
    const scopeId = await createScope(request, token, `Scope-Hist-${Date.now()}`);
    const riskId = await createRiskWithTriangular(
      request,
      token,
      scopeId,
      `Hist-risk-${Date.now()}`,
    );

    const fetchHistory = async () => {
      const r = await request.get(
        `${API_BASE}/api/v1/risks/${riskId}/simulations`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      expect(r.status()).toBe(200);
      return r.json() as Promise<Array<{ label?: string; iterations: number }>>;
    };

    // Initieel leeg
    expect(await fetchHistory()).toHaveLength(0);

    // Drie runs met labels
    for (let i = 0; i < 3; i++) {
      const r = await request.post(
        `${API_BASE}/api/v1/risks/${riskId}/simulate?iterations=2000&seed=${i}&label=Run-${i}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
      expect(r.status()).toBe(200);
    }

    const history = await fetchHistory();
    expect(history).toHaveLength(3);
    // Nieuwste eerst
    expect(history[0].label).toBe('Run-2');
    expect(history[2].label).toBe('Run-0');
  });
});
