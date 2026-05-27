import { test, expect } from '@playwright/test';
import { loginAsAdmin, TENANT_ID, getDevToken, API_BASE } from './helpers/auth';
import { queryScalar, rowExists } from './helpers/db';

test.describe('Beheer — Bevindingen aanmaken via UI', () => {
  test('UI maakt bevinding aan gekoppeld aan assessment → DB-rij + FK consistent', async ({
    page,
    request,
  }) => {
    // Seed: assessment via API zodat de dropdown vulling heeft
    const token = await getDevToken(request);
    const stamp = Date.now();
    const a = await request.post(`${API_BASE}/api/v1/assessments/`, {
      data: {
        assessment_type: 'audit',
        domain: 'ISMS',
        status: 'gepland',
        planned_at: '2026-09-01',
      },
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(a.ok(), await a.text()).toBeTruthy();
    const assessmentId = (await a.json()).id;

    await loginAsAdmin(page);
    await page.goto('/beheer/bevindingen');
    await page.waitForLoadState('networkidle');

    await expect(
      page.getByRole('main').getByRole('heading', { name: 'Bevindingen', exact: true }),
    ).toBeVisible({ timeout: 10_000 });

    await page.getByRole('button', { name: 'Nieuwe bevinding', exact: true }).click();
    await expect(
      page.getByRole('heading', { name: 'Nieuwe bevinding' }),
    ).toBeVisible();

    const title = `E2E-finding-${stamp}`;
    await page.getByLabel('Assessment *').selectOption(assessmentId);
    await page.getByLabel('Titel *').fill(title);
    await page.getByLabel('Ernst *').selectOption('hoog');
    await page.getByRole('button', { name: 'Opslaan' }).click();

    // UI: rij verschijnt in tabel
    const row = page.locator('tr', { hasText: title });
    await expect(row).toBeVisible({ timeout: 10_000 });

    // DB-verificatie: FK + tenant + severity
    expect(
      rowExists(
        'ims_findings',
        `title = '${title}' AND assessment_id = '${assessmentId}' ` +
          `AND severity = 'hoog' AND status = 'open' AND tenant_id = '${TENANT_ID}'`,
      ),
    ).toBe(true);

    const severity = queryScalar<string>(
      `SELECT severity FROM ims_findings WHERE title = '${title}';`,
    );
    expect(severity).toBe('hoog');
  });

  test('validatie: zonder verplichte velden toont foutmelding', async ({
    page,
    request,
  }) => {
    // Seed: minstens één assessment zodat de knop enabled is
    const token = await getDevToken(request);
    await request.post(`${API_BASE}/api/v1/assessments/`, {
      data: {
        assessment_type: 'audit',
        domain: 'ISMS',
        status: 'gepland',
        planned_at: '2026-09-15',
      },
      headers: { Authorization: `Bearer ${token}` },
    });

    await loginAsAdmin(page);
    await page.goto('/beheer/bevindingen');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: 'Nieuwe bevinding', exact: true }).click();
    await page.getByRole('button', { name: 'Opslaan' }).click();

    await expect(
      page.getByText('Vul alle verplichte velden in (inclusief assessment).'),
    ).toBeVisible();
  });
});
