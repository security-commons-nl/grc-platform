import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID, getDevToken, API_BASE } from './helpers/auth';
import { queryScalar, rowExists } from './helpers/db';

test.describe('Beheer — Risico extensies (org-unit + custom-fields) via UI', () => {
  test('UI maakt risico aan met org-unit + custom-attributes → DB heeft alle relaties', async ({
    page,
    request,
  }) => {
    const token = await getDevToken(request);
    const stamp = Date.now();

    // Seed: scope + org-unit + custom-field-definitie zodat de UI ze ophaalt
    const scopeResp = await request.post(`${API_BASE}/api/v1/scopes/`, {
      data: { name: `E2E-Scope-${stamp}`, type: 'cluster', domain: 'ISMS' },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(scopeResp.ok(), await scopeResp.text()).toBeTruthy();
    const scopeName = `E2E-Scope-${stamp}`;

    const unitResp = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
      data: { name: `E2E-Unit-${stamp}`, unit_type: 'cluster' },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(unitResp.ok(), await unitResp.text()).toBeTruthy();
    const unitName = `E2E-Unit-${stamp}`;
    const unitId = (await unitResp.json()).id;

    const fieldName = `e2e_kpgm_${stamp}`;
    const displayLabel = `Kadernota-programma E2E ${stamp}`;
    const cfResp = await request.post(`${API_BASE}/api/v1/custom-fields/`, {
      data: {
        entity_type: 'risk',
        field_name: fieldName,
        display_label: displayLabel,
        json_schema: { type: 'string', maxLength: 100 },
        is_required: false,
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(cfResp.ok(), await cfResp.text()).toBeTruthy();

    // UI-flow
    await loginAsAdmin(page);
    await page.goto('/beheer/risicos');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Nieuw risico', exact: true }).click();
    await page.getByLabel('Scope *').selectOption({ label: scopeName });
    await page.getByLabel('Domein *').selectOption('ISMS');
    const riskTitle = `E2E-risico-${stamp}`;
    await page.getByLabel('Titel *').fill(riskTitle);

    // RiskMatrix select-mode: kies cel kans=3 (Midden), impact=4 (Hoog) → score 12.
    // Cellen hebben `title="Kans: <label>, Impact: <label> — Score: <n>"`.
    await page.locator('button[title^="Kans: Midden, Impact: Hoog"]').click();

    // Org-unit dropdown — label "Organisatie-eenheid"
    await page.getByLabel('Organisatie-eenheid').first().selectOption({ label: unitName });

    // Custom-field input verschijnt automatisch — gebruik unieke label per run zodat
    // er geen botsing is met definities uit eerdere runs (Input genereert id uit label).
    const cfInput = page.getByLabel(displayLabel);
    await expect(cfInput).toBeVisible({ timeout: 10_000 });
    await cfInput.fill('Programma 7 - Welzijn');

    await page.getByRole('button', { name: 'Opslaan' }).click();

    const row = page.locator('tr', { hasText: riskTitle });
    await expect(row).toBeVisible({ timeout: 10_000 });

    // DB-verificatie: org-unit-FK + custom_attributes-jsonb
    const riskId = queryScalar<string>(
      `SELECT id FROM ims_risks WHERE title = '${riskTitle}' AND tenant_id = '${TENANT_ID}';`,
    );
    expect(riskId).toBeTruthy();

    const dbUnitId = queryScalar<string>(
      `SELECT organizational_unit_id FROM ims_risks WHERE id = '${riskId}';`,
    );
    expect(dbUnitId).toBe(unitId);

    const cfValue = queryScalar<string>(
      `SELECT custom_attributes->>'${fieldName}' FROM ims_risks WHERE id = '${riskId}';`,
    );
    expect(cfValue).toBe('Programma 7 - Welzijn');
  });

  test('Filter UI op org-unit beperkt risico-lijst', async ({ page, request }) => {
    const token = await getDevToken(request);
    const stamp = Date.now();

    // Seed: scope, twee units, twee risico's
    const scopeName = `E2E-FilterScope-${stamp}`;
    const scopeResp = await request.post(`${API_BASE}/api/v1/scopes/`, {
      data: { name: scopeName, type: 'cluster', domain: 'ISMS' },
      headers: { Authorization: `Bearer ${token}` },
    });
    const scopeId = (await scopeResp.json()).id;

    const unitA = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
      data: { name: `E2E-FilterA-${stamp}`, unit_type: 'cluster' },
      headers: { Authorization: `Bearer ${token}` },
    });
    const unitAName = `E2E-FilterA-${stamp}`;
    const unitAId = (await unitA.json()).id;

    const unitB = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
      data: { name: `E2E-FilterB-${stamp}`, unit_type: 'cluster' },
      headers: { Authorization: `Bearer ${token}` },
    });
    const unitBId = (await unitB.json()).id;

    const riskInA = `E2E-InA-${stamp}`;
    const riskInB = `E2E-InB-${stamp}`;
    for (const [title, unitId] of [
      [riskInA, unitAId],
      [riskInB, unitBId],
    ] as const) {
      const r = await request.post(`${API_BASE}/api/v1/risks/`, {
        data: {
          scope_id: scopeId,
          domain: 'ISMS',
          title,
          description: 'filter',
          likelihood: 2,
          impact: 3,
          organizational_unit_id: unitId,
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(r.ok(), await r.text()).toBeTruthy();
    }

    await loginAsAdmin(page);
    await page.goto('/beheer/risicos');
    await page.waitForLoadState('networkidle');

    // Beide zichtbaar zonder filter
    await expect(page.locator('tr', { hasText: riskInA })).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('tr', { hasText: riskInB })).toBeVisible();

    // Filter op unitA
    await page
      .getByLabel('Filter op organisatie-eenheid')
      .selectOption({ label: unitAName });
    await page.waitForLoadState('networkidle');

    await expect(page.locator('tr', { hasText: riskInA })).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('tr', { hasText: riskInB })).toHaveCount(0);
  });
});
