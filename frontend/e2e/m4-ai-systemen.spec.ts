import { test, expect, type APIRequestContext } from '@playwright/test';
import { API_BASE, getDevToken, loginAsAdmin } from './helpers/auth';

// Alias om bestaande test-code te bewaren — gebruikt nu gecachede helper i.p.v.
// een verse dev-token-call per test (RATE_LIMIT_AUTH bedraagt 10/min).
const loginViaUI = loginAsAdmin;

test.describe('M4 — AI-systemenregister', () => {
  test('aanmaken via UI met classifier-advies → tabel + filter werken', async ({
    page,
    request,
  }) => {
    await getDevToken(request); // warmup + verify backend bereikbaar

    await loginViaUI(page);
    await page.goto('/beheer/ai-systemen');
    await page.waitForLoadState('networkidle');

    // Pagina-titel moet zichtbaar zijn (empty-state niet asserten — kan rommel
    // overhouden uit eerdere runs in zelfde test-tenant; deze suite test niet
    // de empty-state-flow). Exact: true om botsing met empty-state-tekst
    // "Nog geen AI-systemen" te vermijden.
    await expect(
      page.getByRole('heading', { name: 'AI-systemen', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    // Form openen
    await page.getByRole('button', { name: 'Nieuw AI-systeem' }).click();
    await expect(page.getByRole('heading', { name: 'Nieuw AI-systeem' })).toBeVisible();

    const systemName = `Klant-chatbot ${Date.now()}`;
    await page.getByLabel('Naam *').fill(systemName);
    await page.getByLabel('Leverancier').fill('OpenAI');
    await page.getByLabel('Systeem-type *').selectOption('chatbot');
    // Beschrijving + Use case zijn textareas zonder htmlFor-koppeling —
    // selectie via placeholder is stabieler dan via label.
    await page
      .getByPlaceholder('Wat doet dit AI-systeem')
      .fill('Chatbot voor klantvragen over WMO-voorzieningen.');
    await page
      .getByPlaceholder('Voor wie en met welk doel')
      .fill('Beantwoordt vragen, draagt complexe gevallen over aan medewerker.');

    // Classifier-advies aanvragen — endpoint is deterministisch keyword-based
    await page.getByRole('button', { name: 'Classificatie-advies opvragen' }).click();
    await expect(page.getByText('Voorgesteld')).toBeVisible({ timeout: 10_000 });

    // Advies overnemen — daarna disable verschijnt
    await page.getByRole('button', { name: 'Advies overnemen' }).click();
    await expect(page.getByRole('button', { name: 'Advies overnemen' })).toBeDisabled();

    // Opslaan
    await page.getByRole('button', { name: 'Opslaan' }).click();

    // Rij moet verschijnen in tabel. De rij bevat zowel de systeem-naam
    // ("Klant-chatbot ...") als het type-badge ("chatbot") — strict-mode-
    // conflict bij `getByText('chatbot')`. Asserteren via de Badge-rol
    // (visueel een span; we matchen via celspecifiek).
    const row = page.locator('tr', { hasText: systemName });
    await expect(row).toBeVisible({ timeout: 10_000 });
    await expect(row.getByText('OpenAI')).toBeVisible();
    // Type-cel: badge bevat exact 'chatbot' zonder andere tekst.
    await expect(row.locator('td').nth(1)).toContainText('chatbot');
  });

  test('filter op risico-categorie verbergt niet-passende systemen', async ({
    page,
    request,
  }) => {
    // Twee AI-systemen aanmaken via API: één 'high', één 'minimal'.
    // Geen opruimen tussen tests — de unieke timestamps in de namen
    // voorkomen botsingen, en filter-assertions zoeken op unieke namen.
    const token = await getDevToken(request);

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
