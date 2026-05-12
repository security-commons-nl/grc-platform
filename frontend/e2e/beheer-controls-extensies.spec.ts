import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID, getDevToken, API_BASE } from './helpers/auth';
import { queryScalar, rowExists } from './helpers/db';

test.describe('Beheer — Controls extensies (org-unit + custom-fields)', () => {
  test('UI maakt control aan met org-unit + custom-attributes → DB heeft alle relaties', async ({
    page,
    request,
  }) => {
    const token = await getDevToken(request);
    const stamp = Date.now();

    // Seed: org-unit + custom-field-definitie zodat de UI ze ophaalt
    const unitResp = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
      data: { name: `E2E-Ctrl-Unit-${stamp}`, unit_type: 'cluster' },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(unitResp.ok(), await unitResp.text()).toBeTruthy();
    const unitName = `E2E-Ctrl-Unit-${stamp}`;
    const unitId = (await unitResp.json()).id;

    const fieldName = `e2e_ctrl_${stamp}`;
    const displayLabel = `E2E controlveld ${stamp}`;
    const cfResp = await request.post(`${API_BASE}/api/v1/custom-fields/`, {
      data: {
        entity_type: 'control',
        field_name: fieldName,
        display_label: displayLabel,
        json_schema: { type: 'string', maxLength: 100 },
        is_required: false,
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(cfResp.ok(), await cfResp.text()).toBeTruthy();

    await loginAsAdmin(page);
    await page.goto('/beheer/controls');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Nieuwe control', exact: true }).click();

    const title = `E2E control extensies ${stamp}`;
    await page.getByLabel('Titel *').fill(title);
    await page.getByLabel('Domein *').selectOption('ISMS');
    await page.getByLabel('Implementatiestatus *').selectOption('operationeel');

    // RFC 0002 — org-unit-koppeling
    await page.getByLabel('Organisatie-eenheid').first().selectOption({ label: unitName });

    // RFC 0001 — custom-field input verschijnt automatisch
    const cfInput = page.getByLabel(displayLabel);
    await expect(cfInput).toBeVisible({ timeout: 10_000 });
    await cfInput.fill('Programma kwetsbaarheidsbeheer');

    await page.getByRole('button', { name: 'Opslaan' }).click();

    const row = page.locator('tr', { hasText: title });
    await expect(row).toBeVisible({ timeout: 10_000 });

    // DB-verificatie: beide velden komen door
    const controlId = queryScalar<string>(
      `SELECT id FROM ims_controls WHERE title = '${title}' AND tenant_id = '${TENANT_ID}';`,
    );
    expect(controlId).toBeTruthy();

    const dbUnitId = queryScalar<string>(
      `SELECT organizational_unit_id FROM ims_controls WHERE id = '${controlId}';`,
    );
    expect(dbUnitId).toBe(unitId);

    const cfValue = queryScalar<string>(
      `SELECT custom_attributes->>'${fieldName}' FROM ims_controls WHERE id = '${controlId}';`,
    );
    expect(cfValue).toBe('Programma kwetsbaarheidsbeheer');
  });

  test('Filter UI op org-unit beperkt control-lijst', async ({ page, request }) => {
    const token = await getDevToken(request);
    const stamp = Date.now();

    // Seed: twee units en twee controls erin
    const unitA = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
      data: { name: `E2E-CtrlFilter-A-${stamp}`, unit_type: 'cluster' },
      headers: { Authorization: `Bearer ${token}` },
    });
    const unitAName = `E2E-CtrlFilter-A-${stamp}`;
    const unitAId = (await unitA.json()).id;

    const unitB = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
      data: { name: `E2E-CtrlFilter-B-${stamp}`, unit_type: 'cluster' },
      headers: { Authorization: `Bearer ${token}` },
    });
    const unitBId = (await unitB.json()).id;

    const ctrlInA = `E2E-Ctrl-InA-${stamp}`;
    const ctrlInB = `E2E-Ctrl-InB-${stamp}`;
    for (const [title, unitId] of [
      [ctrlInA, unitAId],
      [ctrlInB, unitBId],
    ] as const) {
      const r = await request.post(`${API_BASE}/api/v1/controls/`, {
        data: {
          title,
          description: 'filter',
          domain: 'ISMS',
          implementation_status: 'operationeel',
          organizational_unit_id: unitId,
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(r.ok(), await r.text()).toBeTruthy();
    }

    await loginAsAdmin(page);
    await page.goto('/beheer/controls');
    await page.waitForLoadState('networkidle');

    // Beide zichtbaar zonder filter
    await expect(page.locator('tr', { hasText: ctrlInA })).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('tr', { hasText: ctrlInB })).toBeVisible();

    // Filter op unitA
    await page
      .getByLabel('Filter op organisatie-eenheid')
      .selectOption({ label: unitAName });
    await page.waitForLoadState('networkidle');

    await expect(page.locator('tr', { hasText: ctrlInA })).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('tr', { hasText: ctrlInB })).toHaveCount(0);
  });

  test('API: cross-tenant org-unit weigert (422)', async ({ request }) => {
    const token = await getDevToken(request);
    // Een willekeurige UUID die niet bestaat → 422 verwacht.
    const r = await request.post(`${API_BASE}/api/v1/controls/`, {
      data: {
        title: `Cross-tenant ${Date.now()}`,
        description: 'should fail',
        domain: 'ISMS',
        implementation_status: 'gepland',
        organizational_unit_id: '00000000-0000-0000-0000-000000000999',
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(r.status()).toBe(422);
  });
});
