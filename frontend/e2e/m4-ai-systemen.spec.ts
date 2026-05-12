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

async function loginViaUI(page: Page) {
  await page.goto('/login');
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: 'Inloggen' }).click();
  await page.waitForURL(/\/inrichten/, { timeout: 15_000, waitUntil: 'domcontentloaded' });
}

test.describe('M4 — AI-systemenregister', () => {
  test('aanmaken via UI met classifier-advies → tabel + filter werken', async ({
    page,
    request,
  }) => {
    // Schoonmaken: bestaande AI-systemen weggooien zodat tabel-assertions deterministisch zijn.
    const token = await getDevToken(request);
    const existing = await request.get(`${API_BASE}/api/v1/ai-systems/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (existing.ok()) {
      const items = (await existing.json()) as Array<{ id: string }>;
      for (const it of items) {
        await request.delete(`${API_BASE}/api/v1/ai-systems/${it.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    }

    await loginViaUI(page);
    await page.goto('/beheer/ai-systemen');
    await page.waitForLoadState('networkidle');

    // Empty-state moet zichtbaar zijn
    await expect(page.getByText('Nog geen AI-systemen')).toBeVisible({ timeout: 10_000 });

    // Form openen
    await page.getByRole('button', { name: 'Nieuw AI-systeem' }).click();
    await expect(page.getByRole('heading', { name: 'Nieuw AI-systeem' })).toBeVisible();

    const systemName = `Klant-chatbot ${Date.now()}`;
    await page.getByLabel('Naam *').fill(systemName);
    await page.getByLabel('Leverancier').fill('OpenAI');
    await page.getByLabel('Systeem-type *').selectOption('chatbot');
    await page.getByLabel('Beschrijving').fill('Chatbot voor klantvragen over WMO-voorzieningen.');
    await page.getByLabel('Use case').fill('Beantwoordt vragen, draagt complexe gevallen over aan medewerker.');

    // Classifier-advies aanvragen — endpoint is deterministisch keyword-based
    await page.getByRole('button', { name: 'Classificatie-advies opvragen' }).click();
    await expect(page.getByText('Voorgesteld')).toBeVisible({ timeout: 10_000 });

    // Advies overnemen — daarna disable verschijnt
    await page.getByRole('button', { name: 'Advies overnemen' }).click();
    await expect(page.getByRole('button', { name: 'Advies overnemen' })).toBeDisabled();

    // Opslaan
    await page.getByRole('button', { name: 'Opslaan' }).click();

    // Rij moet verschijnen in tabel
    const row = page.locator('tr', { hasText: systemName });
    await expect(row).toBeVisible({ timeout: 10_000 });
    await expect(row.getByText('OpenAI')).toBeVisible();
    await expect(row.getByText('chatbot')).toBeVisible();
  });

  test('filter op risico-categorie verbergt niet-passende systemen', async ({
    page,
    request,
  }) => {
    // Twee AI-systemen aanmaken via API: één 'high', één 'minimal'
    const token = await getDevToken(request);

    // Eerst opruimen
    const existing = await request.get(`${API_BASE}/api/v1/ai-systems/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (existing.ok()) {
      const items = (await existing.json()) as Array<{ id: string }>;
      for (const it of items) {
        await request.delete(`${API_BASE}/api/v1/ai-systems/${it.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    }

    const stamp = Date.now();
    const highName = `Beslis-AI-hoog-${stamp}`;
    const minimalName = `Spell-check-minimaal-${stamp}`;

    await request.post(`${API_BASE}/api/v1/ai-systems/`, {
      data: {
        name: highName,
        system_type: 'decision_support',
        eu_ai_act_risk: 'high',
        deployment_status: 'deployed',
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    await request.post(`${API_BASE}/api/v1/ai-systems/`, {
      data: {
        name: minimalName,
        system_type: 'other',
        eu_ai_act_risk: 'minimal',
        deployment_status: 'deployed',
      },
      headers: { Authorization: `Bearer ${token}` },
    });

    await loginViaUI(page);
    await page.goto('/beheer/ai-systemen');
    await page.waitForLoadState('networkidle');

    // Beide zichtbaar zonder filter
    await expect(page.locator('tr', { hasText: highName })).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('tr', { hasText: minimalName })).toBeVisible();

    // Filter op 'Hoog-risico (bijlage III)'
    await page.getByLabel('Filter op risico').selectOption('high');

    // Alleen de high blijft over
    await expect(page.locator('tr', { hasText: highName })).toBeVisible();
    await expect(page.locator('tr', { hasText: minimalName })).toHaveCount(0);

    // Filters wissen → beide terug
    await page.getByRole('button', { name: 'Filters wissen' }).click();
    await expect(page.locator('tr', { hasText: highName })).toBeVisible();
    await expect(page.locator('tr', { hasText: minimalName })).toBeVisible();
  });

  test('classifier-advies is API-deterministisch (zelfde input → zelfde uitkomst)', async ({
    request,
  }) => {
    const token = await getDevToken(request);

    const callTwice = async () => {
      const a = await request.post(
        `${API_BASE}/api/v1/ai-systems/classify-suggestion`,
        {
          data: {
            system_type: 'decision_support',
            description: 'Beslist over toekenning van bijstandsuitkeringen.',
            use_case: 'Automatische beoordeling met menselijke check.',
          },
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      expect(a.status()).toBe(200);
      return a.json();
    };

    const r1 = await callTwice();
    const r2 = await callTwice();
    expect(r1.suggested_risk).toBe(r2.suggested_risk);
    expect(r1.reasoning).toBe(r2.reasoning);
    expect(r1.triggered_by).toEqual(r2.triggered_by);
  });
});
