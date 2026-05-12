import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID, getDevToken, API_BASE } from './helpers/auth';
import { queryScalar } from './helpers/db';

test.describe('Beheer — Assessments extensies (org-unit + custom-fields)', () => {
  test('UI maakt assessment aan met org-unit + custom-attributes → DB heeft alle relaties', async ({
    page,
    request,
  }) => {
    const token = await getDevToken(request);
    const stamp = Date.now();

    const unitResp = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
      data: { name: `E2E-Assm-Unit-${stamp}`, unit_type: 'cluster' },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(unitResp.ok(), await unitResp.text()).toBeTruthy();
    const unitName = `E2E-Assm-Unit-${stamp}`;
    const unitId = (await unitResp.json()).id;

    const fieldName = `e2e_assm_${stamp}`;
    const displayLabel = `E2E assessmentveld ${stamp}`;
    const cfResp = await request.post(`${API_BASE}/api/v1/custom-fields/`, {
      data: {
        entity_type: 'assessment',
        field_name: fieldName,
        display_label: displayLabel,
        json_schema: { type: 'string', maxLength: 100 },
        is_required: false,
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(cfResp.ok(), await cfResp.text()).toBeTruthy();

    await loginAsAdmin(page);
    await page.goto('/beheer/assessments');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Nieuw assessment', exact: true }).click();
    await page.getByLabel('Type *', { exact: true }).selectOption('audit');
    await page.getByLabel('Domein *').selectOption('ISMS');
    await page.getByLabel('Gepland op').fill('2026-07-01');

    // RFC 0002 — org-unit-koppeling
    await page.getByLabel('Organisatie-eenheid').first().selectOption({ label: unitName });

    // RFC 0001 — custom-field
    const cfInput = page.getByLabel(displayLabel);
    await expect(cfInput).toBeVisible({ timeout: 10_000 });
    await cfInput.fill('Jaarprogramma 2026');

    await page.getByRole('button', { name: 'Opslaan' }).click();

    // Eén unieke rij — assessment_type=audit zou met andere tests kunnen
    // botsen, dus filter op de planned_at-datum als bredere sanity-check.
    await expect(page.locator('tr', { hasText: 'audit' }).first()).toBeVisible({
      timeout: 10_000,
    });

    // DB-check: een audit met org-unit + custom-attr op gegeven datum bestaat.
    const assessmentId = queryScalar<string>(
      `SELECT id FROM ims_assessments WHERE assessment_type = 'audit' ` +
        `AND DATE(planned_at) = '2026-07-01' AND organizational_unit_id = '${unitId}' ` +
        `AND tenant_id = '${TENANT_ID}';`,
    );
    expect(assessmentId).toBeTruthy();

    const cfValue = queryScalar<string>(
      `SELECT custom_attributes->>'${fieldName}' FROM ims_assessments WHERE id = '${assessmentId}';`,
    );
    expect(cfValue).toBe('Jaarprogramma 2026');
  });

  test('API: filter ?organizational_unit_id beperkt resultaten', async ({ request }) => {
    const token = await getDevToken(request);
    const stamp = Date.now();

    const unitResp = await request.post(`${API_BASE}/api/v1/organizational-units/`, {
      data: { name: `E2E-AssmFilter-${stamp}`, unit_type: 'cluster' },
      headers: { Authorization: `Bearer ${token}` },
    });
    const unitId = (await unitResp.json()).id;

    // Twee assessments: één in unit, één buiten
    const inUnit = await request.post(`${API_BASE}/api/v1/assessments/`, {
      data: {
        assessment_type: 'audit',
        domain: 'ISMS',
        status: 'gepland',
        planned_at: '2026-08-01',
        organizational_unit_id: unitId,
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(inUnit.ok(), await inUnit.text()).toBeTruthy();
    const inUnitId = (await inUnit.json()).id;

    const outUnit = await request.post(`${API_BASE}/api/v1/assessments/`, {
      data: {
        assessment_type: 'audit',
        domain: 'ISMS',
        status: 'gepland',
        planned_at: '2026-08-01',
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(outUnit.ok(), await outUnit.text()).toBeTruthy();
    const outUnitId = (await outUnit.json()).id;

    const filtered = await request.get(
      `${API_BASE}/api/v1/assessments/?organizational_unit_id=${unitId}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    expect(filtered.ok()).toBeTruthy();
    const ids = ((await filtered.json()) as Array<{ id: string }>).map((a) => a.id);
    expect(ids).toContain(inUnitId);
    expect(ids).not.toContain(outUnitId);
  });

  test('API: cross-tenant org-unit weigert (422)', async ({ request }) => {
    const token = await getDevToken(request);
    const r = await request.post(`${API_BASE}/api/v1/assessments/`, {
      data: {
        assessment_type: 'audit',
        domain: 'ISMS',
        status: 'gepland',
        planned_at: '2026-08-15',
        organizational_unit_id: '00000000-0000-0000-0000-000000000999',
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(r.status()).toBe(422);
  });
});
