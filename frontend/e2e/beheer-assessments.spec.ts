import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID, getDevToken, API_BASE } from './helpers/auth';
import { queryScalar, rowExists } from './helpers/db';

test.describe('Beheer — Assessments + Bevindingen + Bewijs', () => {
  test('UI maakt assessment aan → DB rij + status gepland', async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/beheer/assessments');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Assessments', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    await page.getByRole('button', { name: 'Nieuw assessment', exact: true }).click();
    await page.getByLabel('Type *', { exact: true }).selectOption('audit');
    await page.getByLabel('Domein *').selectOption('ISMS');
    await page.getByLabel('Gepland op').fill('2026-06-15');
    await page.getByRole('button', { name: 'Opslaan' }).click();

    // Wacht op rij in tabel (assessment_type wordt getoond)
    const row = page.locator('tr', { hasText: 'audit' }).first();
    await expect(row).toBeVisible({ timeout: 10_000 });

    // DB-check: minstens één assessment gepland op die datum
    const count = queryScalar<string>(
      `SELECT COUNT(*) FROM ims_assessments WHERE assessment_type = 'audit' AND domain = 'ISMS' ` +
        `AND DATE(planned_at) = '2026-06-15' AND status = 'gepland' AND tenant_id = '${TENANT_ID}';`,
    );
    expect(Number(count)).toBeGreaterThanOrEqual(1);
  });

  test('Bevindingen-filter werkt op API + UI (severity)', async ({ page, request }) => {
    // Seed: maak via API een assessment en daaraan twee bevindingen met verschillende severity
    const token = await getDevToken(request);
    const stamp = Date.now();

    const a = await request.post(`${API_BASE}/api/v1/assessments/`, {
      data: {
        assessment_type: 'audit',
        domain: 'ISMS',
        status: 'gepland',
        planned_at: '2026-07-01',
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(a.ok(), await a.text()).toBeTruthy();
    const assessmentId = (await a.json()).id;

    const titleHigh = `E2E-hoog-${stamp}`;
    const titleLow = `E2E-laag-${stamp}`;

    for (const [title, severity] of [
      [titleHigh, 'hoog'],
      [titleLow, 'laag'],
    ] as const) {
      const r = await request.post(`${API_BASE}/api/v1/assessments/findings/`, {
        data: {
          assessment_id: assessmentId,
          title,
          description: 'E2E filter-test',
          severity,
          status: 'open',
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(r.ok(), await r.text()).toBeTruthy();
    }

    await loginAsAdmin(page);
    await page.goto('/beheer/bevindingen');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('tr', { hasText: titleHigh })).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('tr', { hasText: titleLow })).toBeVisible();

    // Filter op severity = 'hoog' → laag-rij verdwijnt
    await page.getByLabel('Ernst').selectOption('hoog');
    await expect(page.locator('tr', { hasText: titleHigh })).toBeVisible();
    await expect(page.locator('tr', { hasText: titleLow })).toHaveCount(0);
  });

  test('Bewijs UI: aanmaken gekoppeld aan control → DB rij + FK consistent', async ({
    page,
    request,
  }) => {
    // Seed control via API zodat dropdown vulling heeft
    const token = await getDevToken(request);
    const stamp = Date.now();
    const controlTitle = `E2E-evidence-host-${stamp}`;
    const c = await request.post(`${API_BASE}/api/v1/controls/`, {
      data: {
        title: controlTitle,
        description: 'host',
        domain: 'ISMS',
        implementation_status: 'operationeel',
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(c.ok(), await c.text()).toBeTruthy();
    const controlId = (await c.json()).id;

    await loginAsAdmin(page);
    await page.goto('/beheer/bewijs');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Nieuw bewijs', exact: true }).click();
    await page.getByLabel('Control *').selectOption(controlId);
    const evidenceTitle = `E2E-evidence-${stamp}`;
    await page.getByLabel('Titel *').fill(evidenceTitle);
    await page.getByLabel('Type *', { exact: true }).selectOption('document');
    await page.getByLabel('Verzameld op *').fill('2026-05-01');
    await page.getByRole('button', { name: 'Opslaan' }).click();

    await expect(page.locator('tr', { hasText: evidenceTitle })).toBeVisible({ timeout: 10_000 });

    expect(
      rowExists(
        'ims_evidence',
        `title = '${evidenceTitle}' AND control_id = '${controlId}' AND tenant_id = '${TENANT_ID}'`,
      ),
    ).toBe(true);
  });
});
